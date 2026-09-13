from pathlib import Path
import ast,json
import numpy as np
import pandas as pd
import nbformat,shap

ROOT = Path(__file__).resolve().parents[1]
root = ROOT / 'audit/publication'
nb=nbformat.read(ROOT / 'notebook.ipynb', as_version=4)
def function_source(name):
    for cell in nb.cells:
        if cell.cell_type=='code':
            for node in ast.parse(cell.source).body:
                if isinstance(node,ast.FunctionDef) and node.name==name:
                    return ast.get_source_segment(cell.source,node)
    raise KeyError(name)

namespace={'np':np,'pd':pd}
exec(function_source('add_snapshot_features'),namespace)
frame=pd.DataFrame({'Total_Trans_Amt':[100.,0.,np.nan,10.],
                    'Total_Trans_Ct':[0.,0.,2.,np.nan],
                    'Contacts_Count_12_mon':[4.,0.,np.nan,3.],
                    'Total_Relationship_Count':[0.,0.,2.,np.nan]})
original=frame.copy(deep=True)
features=namespace['add_snapshot_features'](frame)
pd.testing.assert_frame_equal(frame,original)
assert features.average_ticket.iloc[0]==100 and features.contact_ratio.iloc[0]==4
assert features.average_ticket.iloc[1]==features.contact_ratio.iloc[1]==0
assert features.iloc[2:][['average_ticket','contact_ratio']].isna().all().all()
assert np.isfinite(features[['average_ticket','contact_ratio']].to_numpy()[:2]).all()

# Synthetic arrays test API shapes only; they are never reported as customer-analysis results.
n,p=5,3
positive=np.array([[.01,.02,.03],[.02,-.01,.04],[.03,.03,-.02],[-.01,.02,.01],[.01,.01,.01]])
base=np.array([.8,.2])
probability=base[1]+positive.sum(axis=1)
namespace.update({'transformed_explain':np.zeros((n,p)), 'positive_class':1,'number_of_classes':2})
exec(function_source('resolve_positive_shap'),namespace)
resolve=namespace['resolve_positive_shap']
cases={
    'list แยก class':[-positive,positive],
    'ndarray รูป (ลูกค้า,feature,class)':np.stack([-positive,positive],axis=2),
    'ndarray รูป (class,ลูกค้า,feature)':np.stack([-positive,positive],axis=0),
    'ndarray รูป (ลูกค้า,class,feature)':np.stack([-positive,positive],axis=1),
    'Explanation หลาย class':shap.Explanation(values=np.stack([-positive,positive],axis=2),base_values=np.tile(base,(n,1))),
    'Explanation positive class':shap.Explanation(values=positive,base_values=np.repeat(base[1],n)),
}
results=[]
for name,output in cases.items():
    values,baseline=resolve(output,base,probability)
    np.testing.assert_allclose(values,positive)
    np.testing.assert_allclose(baseline+values.sum(axis=1),probability)
    results.append({'กรณี':name,'ผล':'ผ่าน'})
try:
    resolve([positive,-positive],base,probability)
except ValueError:
    results.append({'กรณี':'สลับ positive/negative class ผิด','ผล':'ปฏิเสธตามที่ควร'})
else:
    raise AssertionError('Wrong class was accepted')
namespace['positive_class']=0
values,baseline=resolve([positive,-positive],np.array([.2,.8]),probability)
np.testing.assert_allclose(values,positive)
results.append({'กรณี':'positive class อยู่ index 0','ผล':'ผ่าน'})
summary={'ข้อจำกัด':'ตรวจตัวแก้รูปทรง SHAP ด้วยข้อมูลจำลอง ไม่ได้ติดตั้งและรัน SHAP ทุกรุ่นจริง และไม่ใช่ผลวิเคราะห์ลูกค้า',
         'การหารด้วยศูนย์และmissingของfeature':'ผ่าน; ไม่มีการแก้ input DataFrame',
         'SHAP_shape_checks':results}
(root/'compatibility_checks.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))
