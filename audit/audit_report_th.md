> **สถานะก่อนเผยแพร่:** รายงานด้านล่างเป็นบันทึก audit ก่อนแก้ไข (57 cells, คะแนนเดิม 9.2/10) เลข Cell และลิงก์อ้าง `notebook_cells.txt` เวอร์ชันนั้น มิใช่ source ของ final notebook ที่แก้แล้ว ประเด็น MINOR ทั้งสามได้รับการแก้และทดสอบซ้ำ ดู [ผลตรวจเผยแพร่ล่าสุด](publication/final_audit_th.md) และ [หลักฐานการรันล่าสุด](publication/execution.json) การปรับลิงก์ให้ portable ไม่เปลี่ยนข้อค้นพบทางสถิติเดิม

# รายงานตรวจสอบ Notebook วิเคราะห์ Customer Churn

**คำตัดสิน: พร้อมใช้ แต่ควรแก้บางจุดก่อนส่ง — คะแนนรวม 9.2/10 สำหรับงานวิชา Business Data Analytics**

ตรวจ [snapshot ของ source ที่ตรวจในรอบก่อน](notebook_cells.txt) ครบ **57 cells: Markdown 31 และ code 26** รันจาก kernel ใหม่ผ่านทั้งหมด ใช้เวลา **26.44 วินาที** รวม cell ส่งออกหลักฐานของผู้ตรวจอีกหนึ่ง cell ไม่มี error หรือ warning ในการรันครั้งนี้ ไม่แก้ไขต้นฉบับ

**ไม่พบ CRITICAL หรือ MAJOR จากเส้นทางโค้ดและผลที่ตรวจได้** การแบ่งข้อมูล, Pipeline ภายใน CV, การเลือก threshold บน Validation, การประเมิน Test ที่ตรึงโมเดลแล้ว และ positive-class SHAP ถูกต้อง จุดที่ควรแก้เป็นระดับ MINOR: ลำดับตรวจ schema, แผนภาพกระบวนการ และคำอธิบาย calibration ในบทสรุป

ผลจริงใช้ **LightGBM** เป็นโมเดลสุดท้าย: Test AP **0.971949**, ROC-AUC **0.993049**, Recall **96.63%**, Precision **77.59%** ส่วน SHAP อธิบาย **Random Forest tuned** และ Notebook ระบุความแตกต่างไว้แล้ว ไม่ควรนำ SHAP ชุดนี้ไปอธิบายการตัดสินใจของ LightGBM

คะแนนสูงหมายถึงจำแนกสถานะใน snapshot นี้ได้ดี ยังไม่พิสูจน์การพยากรณ์ churn ในอนาคต การรักษาลูกค้า หรือกำไรจากแคมเปญ คะแนนไม่ได้ทำหน้าที่แทนการทดลอง

## 1. ขอบเขต หลักฐาน และสิ่งที่ยังยืนยันไม่ได้

เป้าหมายของงานคือประเมินว่าการวิเคราะห์เปลี่ยนข้อมูลลูกค้าเป็นหลักฐานสำหรับออกแบบการทดลอง retention ได้อย่างมีเหตุผล โดยไม่รั่วข้อมูลและไม่ตีความเกินข้อมูล

**ทางเลือกที่เรียบง่ายกว่า:** ไม่จำเป็นต้องสร้าง Notebook ใหม่ โครงหลักทำงานได้ การแก้เฉพาะจุดที่ระบุด้านล่างเพียงพอ การเพิ่มโมเดลหรือกราฟอีกจำนวนมากไม่ได้แก้ข้อจำกัดเรื่องเวลาและเหตุผลเชิงสาเหตุ

| ประเภทหลักฐาน | ตรวจอะไรแล้ว | ขอบเขตคำยืนยัน |
|---|---|---|
| ตรวจโค้ดและข้อความ | ทุก Markdown/code cell, ตัวแปร, inputs, fit/transform, model selection, threshold, SHAP, ข้อสรุป | ครบทั้ง 57 cells; เลข cell ในรายงานนับ Markdown ด้วย |
| ยืนยันด้วยการรันจริง | 26 code cells ตามลำดับใน kernel ใหม่; JSON/schema; Python AST; outputs | ผ่านบนเครื่องนี้ โดยเปลี่ยนเฉพาะ input/output paths ในสำเนารันให้ชี้โฟลเดอร์จำลอง Kaggle |
| คำนวณอย่างอิสระ | Confusion counts, metrics, thresholds 2,028 ค่า, bootstrap 500 รอบ | ตรงกับ Notebook; ความต่าง metrics สูงสุด 1.11×10⁻¹⁶ จาก floating point |
| ทดสอบความทนทานเฉพาะจุด | การหารด้วยศูนย์/missing, SHAP รูปทรงหลายแบบ, positive class index, การปฏิเสธ class ที่สลับผิด | ผ่านการทดสอบฟังก์ชันด้วยข้อมูลจำลอง; ไม่ใช่ผลวิเคราะห์ลูกค้าเพิ่ม |
| ยังไม่ได้ยืนยัน | Runtime บนบริการ Kaggle, sklearn/SHAP ทุกรุ่น, fallback ทุกสาขา | ห้ามสรุปว่าผ่านทุกเวอร์ชันหรือรันบน Kaggle จริงแล้ว |
| ข้อมูลไม่รองรับ | t0, feature cutoff, future horizon, event/censoring date, treatment assignment | ไม่สามารถพิสูจน์ temporal eligibility, future stability, survival หรือ uplift |

Environment ที่รันจริง: Python 3.13.5, numpy 2.4.2, pandas 3.0.0, scikit-learn 1.8.0, matplotlib 3.10.8, seaborn 0.13.2, SHAP 0.52.0, XGBoost 3.4.1 และ LightGBM 4.7.0

ต้นฉบับ SHA-256 ก่อนและหลังตรวจตรงกัน:
`323c968b6aa1ad3874c7fb916b069626aa250b3c315af76a8682a0ca831389d4`

CSV ที่ใช้มาจาก [Kaggle Credit Card Customers](https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers/data) ชื่อ `BankChurners.csv`; SHA-256:
`c91b525a2a6755a1b0b80dad1d0d008ca97ec4df34552c8f47ffa12b6184b779`

ข้อความผลลัพธ์ของการรันใหม่ตรงกับผลฝังในต้นฉบับ ยกเว้น [Cell 54](notebook_cells.txt#L1278) ที่ขนาดไฟล์ `cv_results.csv` เปลี่ยน 5,494 เป็น 5,490 bytes เพราะค่าจับเวลารันเปลี่ยน ไม่ใช่คะแนนโมเดลเปลี่ยน ผล CSV ทั้ง 12 ไฟล์ตรงกันเมื่อไม่นับคอลัมน์เวลารัน

ลิงก์ Cell ในรายงานชี้สำเนาข้อความสำหรับตรวจสอบ ซึ่งคัดจากต้นฉบับโดยไม่แก้ source code; ไม่ใช่ Notebook ที่แก้ไขใหม่

## 2. ตารางประเด็นที่พบ

**CRITICAL: ไม่พบ** ข้อผิดพลาดที่ทำให้ evaluation ผิดหรือพบ target/preprocessing/group leakage

**MAJOR: ไม่พบ** ข้อผิดพลาดคำนวณ metric, positive-class SHAP หรือข้อสรุปเชิงสาเหตุที่ทำให้ผลหลักใช้ไม่ได้

Temporal leakage เป็นความเสี่ยงที่ **ข้อมูลนี้ตรวจพิสูจน์ไม่ได้** ไม่ใช่สิ่งที่ประกาศว่าปลอดภัยเพราะลบคอลัมน์ Naive Bayes แล้ว

| Severity | Section / Cell | ประเด็น | เหตุใดจึงสำคัญ | ข้อเสนอแก้ไข |
|---|---|---|---|---|
| MINOR | [Cell 13](notebook_cells.txt#L371), [Cell 17](notebook_cells.txt#L465) | ตรวจชุด predictor schema หลังเริ่ม EDA; `train["Total_Trans_Ct"]` ถูกเรียกก่อน assert schema | ถ้าไฟล์ยังมี target แต่ขาด feature นี้ จะเกิด `KeyError: 'Total_Trans_Ct'` ใน EDA ก่อนแจ้ง schema ชัดเจน ผู้ตรวจยืนยันด้วยสำเนาที่ตัด field นี้ออก; ข้อมูลจริงรอบนี้ไม่เกิดปัญหา | ย้ายการตรวจ required columns และชนิดข้อมูลที่จำเป็นไปหลังโหลด/ตรวจ target ก่อน EDA; จะย้าย leakage audit มาหลัง split และก่อน EDA ก็ได้ |
| MINOR | [Cell 1](notebook_cells.txt#L2) เทียบ [Cell 11](notebook_cells.txt#L346) | แผนภาพวาง EDA และ feature engineering ก่อน Train/Validation/Test แม้โค้ดทำถูกและมีข้อความแก้ความเข้าใจ | ผู้อ่านที่ดูแผนภาพอย่างเดียวอาจเรียนรู้ลำดับที่ไม่ปลอดภัย | แก้แผนภาพให้ split อยู่ก่อน training-only EDA ให้ตรงการทำงานจริง |
| MINOR | [Cell 38](notebook_cells.txt#L888), [Cell 57](notebook_cells.txt#L1328) | บทสรุป calibration เน้นค่าเฉลี่ยคลาดเคลื่อน 2.27 จุดเปอร์เซ็นต์ แต่ไม่ชี้กลุ่มที่คะแนนเฉลี่ย 70.16% เทียบ churn จริง 55.94% | ค่าเฉลี่ยรวมอาจทำให้ดูว่าความคลาดเคลื่อนเล็กกว่าที่เกิดในบางช่วง แม้ตารางและรูปแสดงข้อมูลถูกต้องแล้ว | เพิ่มผลของ bin สำคัญและ n ในบทสรุป พร้อมย้ำว่า score ยังไม่พร้อมแทนความน่าจะเป็นจริงสำหรับคำนวณ CLV/มูลค่า; ถ้าจะ recalibrate ให้ใช้ข้อมูลฝึก/validation กับ holdout ใหม่ |
| INFO | [Cell 41](notebook_cells.txt#L1016), [Cell 54](notebook_cells.txt#L1278) | `shap_global_importance.csv` ไม่มีชื่อโมเดล/class/output scale ในตัวไฟล์; ต้องอ่านร่วม manifest | เมื่อแยก CSV ออกจาก Notebook อาจสับสนว่า SHAP เป็นของ LightGBM ทั้งที่เป็น Random Forest | เพิ่ม metadata เหล่านี้ใน export หรือแนบคำอธิบายการจับคู่ไฟล์; ใน Notebook ปัจจุบันระบุแยกโมเดลถูกแล้ว |
| INFO | [Cell 19](notebook_cells.txt#L503), [Cell 30](notebook_cells.txt#L705) | ratios ซ้ำสารสนเทศกับ parents; `Credit_Limit − Total_Revolving_Bal = Avg_Open_To_Buy` แทบตรงเชิงตัวเลข | Coefficients/odds multipliers ไม่ใช่ผลจากการขยับ feature อย่างเป็นอิสระที่เกิดขึ้นได้เสมอ และ SHAP อาจแบ่งเครดิต | ระบุความสัมพันธ์แน่นอนนี้เพิ่ม; ถ้าจะพิสูจน์ประโยชน์ ratio ให้ทำ ablation ใน Train CV ในงานรอบใหม่ ไม่ใช้ Test ปัจจุบันเลือก feature |
| INFO | [Cell 28](notebook_cells.txt#L667), [Cell 30](notebook_cells.txt#L705) | Random Forest ค้น 12 configurations แต่ boosting ใช้สูตรตั้งค่าเดียว และยังไม่มี paired uncertainty สำหรับความต่างระหว่างโมเดล | อันดับนี้เปรียบเทียบสูตรที่ทดลองจริง ไม่ใช่ข้อพิสูจน์ว่า algorithm ใดดีที่สุดอย่างมีนัยสำคัญ | คงถ้อยคำ “ดีที่สุดในสูตรที่ประเมิน”; หากต้องการข้อสรุปเทียบ algorithm ให้กำหนดงบ tuning/paired comparison ล่วงหน้าและใช้การประเมินใหม่ |

รายการ INFO เป็นการเสริมคุณภาพ ไม่ใช่หลักฐานว่า metrics ปัจจุบันผิด ไม่จำเป็นต้องเพิ่มทุกอย่างเพื่อให้งานวิชาผ่าน

## 3. ประเมินลำดับการวิเคราะห์

| ขั้นตอน | คำตัดสิน | เหตุผล |
|---|---|---|
| Business understanding และขอบเขต snapshot | ✅ ถูกต้องและควรคงไว้ | อธิบายมูลค่าก่อน modeling และไม่สร้าง CLV/ROI ปลอม |
| โหลดข้อมูลและ integrity audit | ⚠️ ใช้ได้แต่ควรปรับ | ตรวจ source/key/target ดี; ควรตรวจ required feature schema ให้ครบก่อน EDA |
| Target mapping | ✅ ถูกต้องและควรคงไว้ | ตรวจชื่อกลุ่มก่อน map; Churn=1 คือ Attrited Customer |
| Stratified split | ✅ ถูกต้องและควรคงไว้ | อยู่ก่อน fitted preprocessing และ training-only EDA |
| Training-only EDA | ✅ ถูกต้องและควรคงไว้ | ใช้ Train จริง; ไม่มีการนำ bins ของ EDA ไป fit จาก Test |
| ตำแหน่ง required-schema check | ❌ ควรเปลี่ยนลำดับ | ย้ายมาตรวจหลังโหลดก่อน EDA; เป็นความทนทานของโค้ด ไม่ใช่ leakage ที่พบในรอบนี้ |
| Leakage audit | ⚠️ ใช้ได้แต่ควรปรับ | ปัจจุบันลบ target-derived fields ก่อน modeling ทันเวลา; ย้ายก่อน EDA จะอ่านและตรวจง่ายขึ้น |
| Feature engineering | ✅ ถูกต้องและควรคงไว้ | Row-local function อยู่ใน Pipeline และใช้เหมือนกันทุกชุด |
| Preprocessing + CV | ✅ ถูกต้องและควรคงไว้ | Imputer/scaler/encoder ถูก fit ใหม่เฉพาะ training fold |
| Baselines + tuning | ✅ ถูกต้องและควรคงไว้ | เปรียบเทียบสูตรง่ายถึงซับซ้อน; tuning ใช้ Train อย่างเดียว |
| Model selection บน Validation | ✅ ถูกต้องและควรคงไว้ | ใช้เลือก model family ได้ เพราะ Test ยังแยกไว้; ไม่ใช่ leakage โดยตัวมันเอง |
| Threshold บน Validation | ✅ ถูกต้องและควรคงไว้ | เลือกตาม cost ที่ประกาศ แล้วตรึงก่อน Test |
| Test evaluation | ✅ ถูกต้องและควรคงไว้ | ตรึง model/threshold; ใช้ predictions ชุดเดิมใน diagnostics |
| Calibration หลัง Test | ✅ ถูกต้องและควรคงไว้ | เป็นการประเมิน ไม่ใช่ fit recalibrator บน Test |
| SHAP หลัง Test | ✅ ถูกต้องและควรคงไว้ | ใช้ forest ที่ fit แล้ว; ไม่ปรับ model และไม่เลือกคนจาก label |
| Business hypotheses / experiment / monitoring | ✅ ถูกต้องและควรคงไว้ | แยกการทำนายออกจากผลการรักษาลูกค้าอย่างสม่ำเสมอ |

**ลำดับปัจจุบันของโค้ดจริง**

Business → โหลด/ตรวจข้อมูลและ target → Split → EDA บน Train → Leakage/schema audit → Features/Pipeline → CV/tuning บน Train → เลือกโมเดลและ threshold บน Validation → Frozen Test → Calibration/SHAP → Hypotheses/Experiment/Monitoring

**ลำดับที่แนะนำ โดยเปลี่ยนเฉพาะจุดจำเป็น**

Business → โหลด/ตรวจข้อมูล **รวม required schema** → Target → Split → Leakage audit → EDA บน Train → Features/Pipeline → ขั้นตอนที่เหลือเหมือนเดิม

การตรวจ missingness/duplicates และรายงาน prevalence ทั้งแหล่งก่อน split ใช้บรรยายสถาปัตยกรรมข้อมูล ไม่ใช่การ fit preprocessing การใช้ Validation ทั้งเลือก model family และ threshold เพิ่มความเสี่ยง selection optimism ของ Validation แต่มี Test อิสระรองรับอยู่ จึงไม่จำเป็นต้องสร้าง split เพิ่มเพียงเพราะลำดับไม่เหมือนตัวอย่างทุกจุด

## 4. ภาพรวมข้อมูลและ baseline

หลักฐาน: [Cell 5](notebook_cells.txt#L184)–[Cell 11](notebook_cells.txt#L346) และ `partition_summary.csv`

| รายการ | ผลจริง |
|---|---:|
| แถวข้อมูล/ลูกค้าไม่ซ้ำ | 10,127 |
| คอลัมน์ต้นทางทั้งหมด | 23 |
| Retained | 8,500 |
| Churned | 1,627 |
| Churn prevalence ใน snapshot | 16.06596% |
| Retained prevalence / majority accuracy | 83.93404% |
| Predictor ต้นทางหลังตัด ID, target, Naive Bayes 2 fields | 19 |
| Engineered features | 2 |
| Predictor หลังเพิ่ม features | 21: numeric 16 และ categorical 5 |
| คอลัมน์หลัง one-hot encoding | 39 |
| Missing cells แบบ NaN | 0 |
| Infinite values / ค่าผิด range ที่ตรวจไว้ | 0 / 0 |
| Exact duplicate rows / duplicate CLIENTNUM | 0 / 0 |
| Feature profiles ซ้ำทั้งชุดก่อนเพิ่ม ratios | 0 |

`Unknown` เป็นค่าหมวดหมู่จริง: Education_Level **1,519**, Marital_Status **749**, Income_Category **1,112** รวม **3,380 cells** ตัวเลขนี้ไม่ใช่จำนวนลูกค้าไม่ซ้ำ และไม่ควรถูกนับรวมกับ NaN โดยอัตโนมัติ

ค่าประวัติ 10,127/23/1,627 ใน Notebook เป็นตัวเปรียบเทียบ ไม่ใช่ค่าที่บังคับผลการคำนวณ รอบนี้ค่าจริงตรงกับ reference

| ชุดข้อมูล | n | Churn | Prevalence |
|---|---:|---:|---:|
| Train | 6,076 | 976 | 16.0632% |
| Validation | 2,025 | 325 | 16.0494% |
| Test | 2,026 | 326 | 16.0908% |

ใช้ seed 42 และ stratification ทั้งสองครั้ง ไม่พบ `CLIENTNUM` ทับซ้อนระหว่างคู่ชุดใด การทำนายทุกคนว่า retained ให้ accuracy สูงถึงประมาณ 83.9% แต่ churn recall เป็นศูนย์ จึงเป็น baseline ที่จำเป็นสำหรับชี้ว่า **accuracy สูงไม่ได้แปลว่าค้นหาคน churn ได้**

**ข้อจำกัด:** prevalence นี้ไม่ใช่ annual churn rate, monthly churn rate หรือ logo churn ที่มี denominator ณ ต้นช่วงเวลา รายงานช่วงเวลาเช่นนั้นไม่ได้จากข้อมูลชุดนี้

## 5. ผล EDA สำคัญ: ผลลัพธ์บอกอะไร และยังสรุปอะไรไม่ได้

ใช้ Train 6,076 รายจริงตาม [Cell 13](notebook_cells.txt#L371)–[Cell 14](notebook_cells.txt#L404); ไม่พบการใช้ Test เลือกการแบ่งกลุ่มหรือพัฒนา feature

### 5.1 Transaction activity เป็นสัญญาณที่ชัดที่สุดในกลุ่มที่ตรวจ

| Total_Trans_Ct | n | Churn | Churn rate | Wilson 95% CI |
| --- | --- | --- | --- | --- |
| (9.999, 45.0] | 1,585 | 594 | 37.48% | 35.13%–39.89% |
| (45.0, 67.0] | 1,485 | 297 | 20.00% | 18.04%–22.11% |
| (67.0, 81.0] | 1,608 | 67 | 4.17% | 3.29%–5.26% |
| (81.0, 139.0] | 1,398 | 18 | 1.29% | 0.82%–2.03% |

กลุ่มต่ำสุดมี churn **37.48%** เทียบกลุ่มสูงสุด **1.29%** ต่าง **36.19 จุดเปอร์เซ็นต์** กลุ่ม quantile ไม่จำเป็นต้องมี n เท่ากันเพราะ transaction count เป็นจำนวนเต็มและมีค่าซ้ำ การไม่แยกคนที่ count เท่ากันออกเป็นคนละ band เหมาะสมกว่า

**ผลลัพธ์บอกอะไร:** กิจกรรมธุรกรรมต่ำสัมพันธ์กับ attrition ที่พบใน snapshot; เหมาะเป็นตัวแปรจัดอันดับและตั้งสมมติฐาน engagement review

**ยังสรุปอะไรไม่ได้:** เพิ่มธุรกรรมแล้ว churn จะลดลงเท่านี้ หรือ count ≤45 เป็นเกณฑ์ production ที่เหมาะสม ตัวแปรอาจเป็นอาการร่วมของ churn หรือวัดในช่วงใกล้/หลังสถานะ attrition ซึ่งยังไม่มีเวลามาตรวจ

### 5.2 Inactivity มีรูปแบบไม่เป็นเส้นตรง

| Months_Inactive_12_mon | n | Churn | Churn rate |
|---|---:|---:|---:|
| 0 | 14 | 8 | 57.14% |
| 1 | 1,332 | 57 | 4.28% |
| 2 | 1,994 | 317 | 15.90% |
| 3 | 2,308 | 496 | 21.49% |
| 4 | 252 | 73 | 28.97% |
| 5 | 106 | 14 | 13.21% |
| 6 | 70 | 11 | 15.71% |

**ผลลัพธ์บอกอะไร:** ช่วง 1–4 เดือนมีอัตราสูงขึ้น แต่ 5–6 เดือนไม่สูงขึ้นต่อ ความสัมพันธ์จึงไม่ใช่ “ยิ่ง inactive ยิ่งเสี่ยง” ทุกช่วง

**ยังสรุปอะไรไม่ได้:** กลุ่ม 0 เดือน 57.14% มีเพียง 14 คนและ Wilson CI ประมาณ **32.59%–78.62%** ไม่ใช่เหตุผลสำหรับตั้งกฎติดต่ออัตโนมัติ อัตราระดับ 5–6 เดือนก็มีความไม่แน่นอนและ customer mix ต่างกันได้

บทสรุปแบบเทียบเพียง endpoint 1 กับ 6 เดือนใน playbook คำนวณถูก แต่การอธิบายเต็มรูปแบบข้างต้นสะท้อนข้อมูลดีกว่า

### 5.3 Relationship depth และ service contacts

Relationship count 1, 2, 3, 4, 5, 6 มี churn ตามลำดับ **25.81%, 29.10%, 16.85%, 11.98%, 11.05%, 11.15%** กลุ่ม 1–2 relationships เสี่ยงสูงกว่ากลุ่ม 4–6 ในข้อมูลนี้ แต่ไม่ได้เพิ่มหรือลดแบบ monotonic ทุกขั้น

Contacts count 0, 1, 2, 3, 4, 5 มี churn **1.63%, 6.76%, 13.16%, 19.58%, 24.06%, 32.69%** กลุ่ม 6 contacts มี **24/24 ราย churn** แต่ n=24 ต่ำกว่าเกณฑ์ 30 จึงไม่ควรใช้ 100% เป็นกฎเด็ดขาด Notebook ตัดกลุ่มเล็กนี้ออกจาก endpoint comparison ของ playbook อย่างเหมาะสม

**ผลลัพธ์บอกอะไร:** จำนวนความสัมพันธ์ต่ำและการติดต่อบ่อยสัมพันธ์กับ observed churn เป็นจุดตั้งสมมติฐานเรื่องความต้องการที่ยังไม่ได้ตอบหรือปัญหาบริการ

**ยังสรุปอะไรไม่ได้:** การเพิ่มผลิตภัณฑ์หรือการลดจำนวนการติดต่อจะรักษาลูกค้าได้ การติดต่ออาจเป็นผลของปัญหาหรือการเลิกใช้บริการอยู่แล้ว และ source ไม่บอกทิศทาง/เหตุผลการติดต่อ

### 5.4 พฤติกรรม การเงิน และ customer mix อื่น

| Feature | Median ของ retained ใน Train | Median ของ churned ใน Train | อ่านอย่างไร |
|---|---:|---:|---|
| Total_Trans_Amt | 4,098 | 2,312.5 | กลุ่ม churn ใช้จ่ายน้อยกว่า; หน่วยเงินและ cutoff ที่แน่นอนไม่ได้ยืนยันจาก CSV |
| Total_Ct_Chng_Q4_Q1 | 0.722 | 0.533 | Count change measure ของกลุ่ม churn ต่ำกว่า |
| Total_Amt_Chng_Q4_Q1 | 0.743 | 0.703 | Amount change ต่างกันน้อยกว่าตัว count; ไม่ใช่ผลเชิงสาเหตุ |
| Avg_Utilization_Ratio | 0.2135 | 0 | กลุ่ม churn มี utilization ต่ำกว่าใน median |
| Total_Revolving_Bal | 1,375 | 0 | Median balance ของ churn เป็นศูนย์; อาจสัมพันธ์กับการหยุดใช้งาน/ปิดความสัมพันธ์ |
| Credit_Limit | 4,644 | 4,145.5 | ความต่างเล็กกว่า behavioral signals; ต้องดู distribution และตัวแปรร่วม |
| Contacts_Count_12_mon | 2 | 3 | กลุ่ม churn ติดต่อบ่อยกว่า |
| Months_on_book | 36 | 36 | Median เท่ากัน ไม่ได้แปลว่า distribution เท่ากันหรือไม่มี conditional signal |
| Customer_Age | 46 | 46 | Median ไม่แบ่งกลุ่มชัด ไม่ใช่หลักฐานว่าอายุไม่มีความสัมพันธ์ทุกแบบ |

Gender F กับ M มี churn **17.73% กับ 14.19%** ใน Train; Card Platinum **3/11 = 27.27%** เทียบ Blue **910/5,664 = 16.07%** ต้องระวังขนาด Platinum ที่เล็กมาก

Income_Category ต่ำกว่า $40K มี **17.79%** เทียบ $60K–$80K **14.06%**; Education Doctorate **21.27%** เทียบ High School **14.29%**; Marital_Status Unknown **18.49%** เทียบ Married **15.35%** ทั้งหมดเป็น marginal associations ที่อาจอธิบายด้วย customer mix และตัวแปรสัมพันธ์อื่น ห้ามตีความเป็นเหตุผลในการเลือกปฏิบัติหรือผลของการเปลี่ยนคุณลักษณะส่วนบุคคล

### 5.5 คุณภาพการใช้สถิติและกราฟ

กราฟ transaction quartiles, inactivity, relationship depth, PR/ROC, calibration และ SHAP มีหน้าที่ต่างกัน ไม่พบการทำกราฟจำนวนมากโดยไร้ประเด็นทั้งหมด แต่ categorical panel และ boxplot 3×3 ควรอ่านร่วมตารางและคำอธิบายเฉพาะตัวแปร

Wilson intervals มีสูตรถูกต้องและแสดง small-n flags; เป็น intervals รายกลุ่มที่ยังไม่แก้ multiple comparisons Notebook ไม่รัน chi-square โดยไม่ตรวจ expected frequencies และไม่ตีความ correlation เป็น causal effect ข้ออภิปรายเรื่อง cross-tab หลายมิติมี sparse cells/multiple testing ถูกต้อง

## 6. Feature engineering และ preprocessing

หลักฐาน: [Cell 18](notebook_cells.txt#L491)–[Cell 22](notebook_cells.txt#L559)

| Feature | สูตร | ผลตรวจ | ความหมายและขอบเขต |
|---|---|---|---|
| average_ticket | `Total_Trans_Amt / Total_Trans_Ct.clip(lower=1)` | สูตรตรงโจทย์; NaN/inf ที่เกิดใหม่ 0 | จำนวนเงินต่อธุรกรรม; เมื่อ count=0 เป็น proxy ตามกติกา denominator ไม่ใช่ ticket ที่สังเกตจริง |
| contact_ratio | `Contacts_Count_12_mon / Total_Relationship_Count.clip(lower=1)` | สูตรตรงโจทย์; NaN/inf ที่เกิดใหม่ 0 | ความเข้มข้นการติดต่อเทียบความลึกความสัมพันธ์; ยังไม่ใช่ตัววัดปัญหาบริการโดยตรง |

ฟังก์ชันสร้างสำเนา DataFrame ไม่แก้ input ต้นทาง การทดสอบ denominator=0, missing numerator และ missing denominator ผ่าน โดย missing ที่มาจาก source ยังคงไว้เพื่อให้ imputer ใน fold จัดการ ไม่ได้สร้าง rolling/trend/RFM ปลอมจาก snapshot

Train correlation ของ `average_ticket` กับ `Total_Trans_Amt` = **0.9060**, กับ `Total_Trans_Ct` = **0.5350**; `contact_ratio` กับ `Total_Relationship_Count` = **−0.6584**, กับ contact count = **0.4982** จึงมีสารสนเทศร่วมสูงแต่ไม่ใช่คอลัมน์ค่าซ้ำตรงกัน

นอกจากนี้ `Credit_Limit − Total_Revolving_Bal = Avg_Open_To_Buy` คลาดเคลื่อนสูงสุดเพียง **5.68×10⁻¹⁴** ใน source ที่ตรวจ เป็นความซ้ำซ้อนเชิงพีชคณิต ไม่ใช่เพียง “correlation สูง” โมเดล regularized/ต้นไม้ยัง fit ได้ แต่แยกความหมาย coefficient รายตัวได้ยาก

**ตัดสินประโยชน์:** ratios มีความหมายและใช้งานได้ แต่ยังไม่พิสูจน์ว่าช่วยเพิ่ม AP เพราะไม่มี ablation แบบมี/ไม่มี ratios บน folds เดียวกัน ห้ามอ้างว่า SHAP ของ ratio สูงเป็นหลักฐานว่าเพิ่ม performance แล้ว

Pipeline ถูกต้อง: `FunctionTransformer(add_snapshot_features)` แล้ว `ColumnTransformer` แล้ว estimator; numeric เป็น median imputation + StandardScaler; categorical เป็น most-frequent imputation + OneHotEncoder(handle_unknown="ignore") Dense output ใช้กับทุกโมเดลและ SHAP ได้จริง; feature names คืนได้ครบ 39 ชื่อ

การหา numeric/categorical columns ใช้ Train หลัง feature creation; `clone(preprocessor)` อยู่ในแต่ละ estimator Pipeline และ sklearn fit ใหม่ทุก CV fold ไม่พบการ fit scaler/imputer/encoder บน Validation หรือ Test การใช้ scaler กับ trees ไม่จำเป็นทางคณิตศาสตร์ แต่ไม่ได้ทำให้ workflow นี้รั่วข้อมูล

**Logistic interpretation:** เช่น `average_ticket` มี coefficient **2.2549**, odds multiplier **9.5340** ต่อหนึ่ง training SD ในพิกัดโมเดล แต่ไม่ใช่การเพิ่ม average ticket จริงโดยตรึง amount/count ทุกตัวพร้อมกันได้ และไม่ใช่ “เพิ่มโอกาส churn 9.53 เท่า” Odds ไม่ใช่ probability; การเทียบระดับ category ต้องใช้ส่วนต่าง coefficients ตามที่ Notebook อธิบายไว้

## 7. Leakage audit และความถูกต้องของการแบ่งข้อมูล

หลักฐาน: [Cell 5](notebook_cells.txt#L184), [Cell 11](notebook_cells.txt#L346), [Cell 17](notebook_cells.txt#L465), [Cell 22](notebook_cells.txt#L559), [Cell 28](notebook_cells.txt#L667), [Cell 30](notebook_cells.txt#L705), [Cell 32](notebook_cells.txt#L753), [Cell 34](notebook_cells.txt#L818)

| Leakage ประเภท | ผลตรวจ | ข้อสรุปที่อนุญาต |
|---|---|---|
| Target | ตัด `Attrition_Flag`, `Churn`, `CLIENTNUM` และทั้งสอง field ที่ match `Naive_Bayes_Classifier_Attrition_Flag` ก่อนสร้าง X | ไม่พบ target-derived output เหล่านี้ใน predictor 19 ตัว |
| Temporal | ไม่มี feature/event timestamps หรือ label horizon ที่ตรวจย้อนกลับได้ | ยืนยันว่าไม่มี temporal leakage ไม่ได้; จำกัดข้อสรุปไว้ที่ snapshot |
| Preprocessing | CV รับเฉพาะ X_train/y_train; preprocessing อยู่ใน Pipeline | ไม่พบ imputer/scaler/encoder เห็น Validation/Test ตอน fit |
| Group | CLIENTNUM unique และ intersections ของ Train/Validation/Test ทุกคู่เป็นศูนย์ | ไม่พบลูกค้าคนเดียวข้าม partition ตาม key ที่มี |

มีการตรวจชื่อ predictor ที่น่าสงสัยและ exact/inverted target copies บน Train ไม่พบคอลัมน์ผิดกลุ่ม การตรวจเช่นนี้ไม่ได้ครอบคลุม proxy target ทุกรูปแบบ แต่ whitelist ชื่อ source fields ช่วยป้องกันคอลัมน์ใหม่หลุดเข้ามา

**AP สูงน่าสงสัยหรือไม่:** ผู้ตรวจติดตามการลบ Naive Bayes outputs, พารามิเตอร์ fit, fold indices และ class mapping แล้ว ไม่พบเส้นทาง code leakage ที่อธิบายคะแนนสูง คะแนนอาจสูงเพราะตัวแปรกิจกรรมใน snapshot แยกสถานะ attrition ได้มาก อย่างไรก็ดี ไม่สามารถตัดความเป็นไปได้ว่าพฤติกรรมบางตัวสะท้อนสถานะ churn ที่เกิดแล้วหรือเกิดร่วมกันได้

การเรียก forest probabilities บน Test เพิ่มใน SHAP เมื่อ final model เป็น LightGBM **ไม่ใช่การประเมิน Test หลายโมเดลเพื่อเลือกผู้ชนะ** เพราะไม่ใช้ forest test labels คำนวณ leaderboard/cost และไม่มีการเปลี่ยน policy หลังดูผล ส่วน metrics, bootstrap, calibration และ subgroup diagnostics ใช้ frozen predictions ชุดเดิมตามวัตถุประสงค์ที่ประกาศ

## 8. ผลเปรียบเทียบโมเดลและ class imbalance

หลักฐาน: [Cell 23](notebook_cells.txt#L586)–[Cell 30](notebook_cells.txt#L705)

| โมเดล | CV AP | Validation AP | Validation ROC-AUC | Validation Brier | Final |
| --- | --- | --- | --- | --- | --- |
| LightGBM benchmark | 0.963839 | 0.967595 | 0.993184 | 0.026384 | เลือก |
| XGBoost benchmark | 0.953016 | 0.954549 | 0.990460 | 0.026774 | — |
| Random Forest tuned | 0.942576 | 0.943733 | 0.987405 | 0.035340 | — |
| Random Forest baseline | 0.931457 | 0.936431 | 0.985783 | 0.040918 | — |
| Logistic Regression | 0.770088 | 0.803974 | 0.937689 | 0.099024 | — |
| Decision Tree | 0.756127 | 0.781677 | 0.954209 | 0.082517 | — |
| Majority baseline | 0.160632 | 0.160494 | 0.500000 | 0.160494 | — |

Logistic Regression ใช้ `class_weight="balanced"`, L2 regularization ตามค่าเริ่มต้น, max_iter=2000 และไม่พบ convergence warning Decision Tree คุม max_depth=5 และ min_samples_leaf=20; Random Forest baseline ใช้ 150 trees, depth=10, leaf=2 พร้อม balanced weights

LightGBM ดีสุดทั้ง Train CV AP และ Validation AP/ROC-AUC ในสูตรที่เปรียบเทียบ และมี Validation Brier ต่ำสุด จึงเป็นตัวเลือกที่มีเหตุผล ไม่ใช่เลือกเพราะชื่อดูซับซ้อน

กติกาที่ประกาศก่อนเปิด Test คือเก็บ course forest หาก AP ตามหลังผู้ชนะไม่เกิน 0.01 และ Brier แย่กว่าไม่เกิน 0.02 รอบนี้ forest AP ตามหลัง LightGBM **0.023862** จึงไม่ผ่านเกณฑ์แรก โมเดลสุดท้ายจึงเป็น LightGBM ส่วน Random Forest เก็บไว้สำหรับ TreeSHAP

กติกานี้เป็น practical tolerance ไม่ใช่ significance test ยังสรุปว่า LightGBM เหนือกว่าอย่างมีนัยสำคัญทางสถิติหรือดีที่สุดในทุกช่วงเวลาไม่ได้ CV ของสูตรต่าง ๆ ใช้ข้อมูล/folds/AP เหมือนกัน แต่มีงบ tuning ต่างกันและ XGBoost เป็น unweighted recipe ขณะที่ LightGBM มี class weighting ทั้งหมดเปิดเผยไว้แล้ว

XGBoost และ LightGBM รับ encoded numeric matrix จริง ไม่มี early stopping จึงไม่มี validation-set access ผ่าน early stopping ให้ตรวจเพิ่มเติม ขั้นตอน optional import ข้ามได้เมื่อไม่พบไลบรารี; รอบ audit นี้ทั้งสอง package ใช้งานได้จริง แต่ไม่ได้รันทุกรุ่นย้อนหลัง

**Imbalance:** Balanced weights คำนวณภายในแต่ละ fit ไม่ใช่ใช้ target ของทั้ง dataset มาให้ fold การให้น้ำหนักช่วยเน้น minority class แต่เปลี่ยนการ fit จึงต้องประเมิน probability calibration SMOTE/ADASYN/SMOTENC อยู่เฉพาะเนื้อหาอธิบาย ไม่มี oversampling ที่เห็น Validation/Test และไม่มีหลักฐานว่าต้องเพิ่ม synthetic sampling เพื่อให้งานนี้ถูกต้อง

## 9. Hyperparameter optimization และความทนทาน

หลักฐาน: [Cell 22](notebook_cells.txt#L559), [Cell 28](notebook_cells.txt#L667) และ `cv_results.csv`

ใช้ `StratifiedKFold(n_splits=3, shuffle=True, random_state=42)` บน Train และเรียกสิ่งนี้ว่า stratified CV ภายใน historical snapshot อย่างถูกต้อง ไม่อ้างว่าเป็น temporal CV

Random Forest grid มี **12 configurations × 3 folds = 36 CV fits** และ refit ผู้ชนะบน Train อีกครั้ง `n_jobs=2` ระดับ search และแต่ละ forest ใช้ worker เดียว ช่วยไม่ให้ซ้อน parallelism จนเกินจำเป็น

ค่าที่เลือกจริง:

```python
{
    "model__n_estimators": 150,
    "model__max_depth": None,
    "model__min_samples_leaf": 2,
    "model__max_features": "sqrt"
}
```

Best mean CV AP = **0.942576**; fold SD = **0.001707**; mean Train AP = **0.999809**; gap = **0.057233** การไม่จำกัด depth มีโอกาสจำรูปแบบ Train มาก แต่ leaf size 2, bootstrap และ random feature subsets ช่วยควบคุม และผลที่นำมาเลือกเป็น held-out fold AP จึงไม่ใช่ใช้ training score เลือกโมเดล

Tuned RF CV AP สูงกว่า baseline **0.011119** การค้นครั้งนี้เหมาะกับขนาดข้อมูลและงานวิชา แต่ 3 folds/หนึ่ง seed ไม่ใช่การทดสอบ stability ครบทุกมิติ และ SD ของ folds ไม่ใช่ CI เพราะ folds ไม่เป็นอิสระทั้งหมด

มีการคำนวณ baseline forest configuration ซ้ำใน grid ซึ่งเป็นค่าใช้จ่ายเล็กน้อยและไม่ทำให้ผลผิด ไม่จำเป็นต้อง refactor ทั้งระบบเพื่อประหยัดไม่กี่ fits

## 10. Threshold selection: ถูกต้องตามต้นทุนสมมติ

หลักฐาน: [Cell 31](notebook_cells.txt#L742)–[Cell 32](notebook_cells.txt#L753); ผู้ตรวจคำนวณทุกแถวใน `validation_threshold_analysis.csv` ใหม่

ใช้ threshold **0.271024392128117** และกติกา `probability >= threshold` จาก Validation เท่านั้น ผู้ตรวจตรวจ **2,028 thresholds** รวม flag-all และ flag-none แล้ว ยืนยันว่าเลือก loss ต่ำสุดจริงตาม tie-break ที่กำหนด

| ผลบน Validation | Threshold ที่เลือก 0.271024 | Threshold 0.50 สำหรับอ้างอิง |
|---|---:|---:|
| TP | 317 | 303 |
| FP | 95 | 48 |
| FN | 8 | 22 |
| TN | 1,605 | 1,652 |
| Precision | 76.94% | 86.32% |
| Recall | 97.54% | 93.23% |
| F1 | 0.860244 | 0.896450 |
| Flagged | 412 (20.35%) | 351 (17.33%) |
| Loss = 5×FN + FP | **135** | **158** |

การลด threshold เพิ่มผู้ถูก flag **61 ราย**, จับ churn เพิ่ม **14 ราย**, แลกกับ FP เพิ่ม **47 ราย** เมื่อ FN แพง 5 หน่วย การลด FN 14 รายลด loss 70 หน่วย แต่ FP เพิ่ม cost 47 หน่วย จึงลด loss สุทธิ **23 หน่วย**

F1 ที่ threshold ใหม่ต่ำกว่า 0.50 **ไม่ใช่ข้อผิดพลาด** เพราะ objective ที่ประกาศคือ cost ไม่ใช่ F1 ควรเลือก metric ให้ตรง decision objective ก่อนดู Test

ทั้งหมดเป็น **ต้นทุนสมมติสำหรับการเรียน ไม่ใช่เศรษฐศาสตร์บริษัทจริง** FP/FN loss ยังไม่รวมต้นทุนติดต่อทุกคน, incentive, โอกาสช่วยได้จริง หรือกำไรจากลูกค้าที่อยู่ต่อ และ score 0.2710 ไม่ได้ยืนยันว่าโอกาส churn จริงของทุกคนที่ได้คะแนนใกล้กันเท่ากับ 27.10%

การสร้าง threshold table ตาม distinct scores ครอบคลุมทุกการแบ่งที่เป็นไปได้ใน Validation แต่การค้นหลาย threshold ทำให้ minimum Validation loss มี selection optimism จึงต้องอ่านคู่ผล frozen Test ด้านล่าง ไม่มีการปรับ threshold หลัง Test ในโค้ดนี้

## 11. Final Test performance และ confusion matrix

หลักฐาน: [Cell 34](notebook_cells.txt#L818), `test_predictions.csv`, `final_metrics.csv` และ [ผลคำนวณอย่างอิสระ](independent_metric_checks.csv)

ผู้ตรวจคำนวณ AP จาก score groups/recall increments, ROC-AUC จาก rank statistic, confusion counts จาก boolean masks และ Brier จาก squared error โดยไม่ใช้ metric function ของ Notebook ในการตรวจค่าหลัก ผลตรงกันทั้งหมด

| Metric | ค่าจริง | ค่านี้คืออะไร | การประเมิน/ประโยชน์ธุรกิจ | ข้อควรระวัง |
| --- | --- | --- | --- | --- |
| Average Precision | 0.971949 | คุณภาพ ranking ตลอด recall increments | สูงกว่า prevalence baseline 0.160908 มาก เหมาะสำหรับจัดลำดับ review | ไม่ใช่ accuracy 97.19% และไม่ใช่ geometric trapezoidal PR-AUC |
| ROC-AUC | 0.993049 | โอกาสที่ churner ถูกจัดอันดับสูงกว่า retained สุ่มหนึ่งคน โดยคิด ties ครึ่งหนึ่ง | แยกสองกลุ่มได้ดีมากใน snapshot | ไม่ระบุต้นทุน/จำนวน false contacts ณ threshold ที่ใช้ |
| Accuracy | 94.9654% | ทำนายถูกทุกคลาสรวมกัน | สูงกว่า majority baseline ประมาณ 83.9% | ไม่ควรใช้ metric นี้เป็นเกณฑ์หลักในข้อมูล imbalanced |
| Balanced Accuracy | 95.6364% | เฉลี่ย Recall ของ churn กับ specificity ของ retained | ทั้งสองคลาสถูกจำแนกได้ดี ไม่ใช่ชนะด้วยคลาสใหญ่เพียงอย่างเดียว | ยังไม่แทน FP/FN costs หรือ treatment value |
| Precision | 77.5862% | ใน 406 flags มี churn จริง 315 ราย | ช่วยให้กลุ่ม review มี churn หนาแน่นกว่าฐานมาก | 22.41% ของ flags เป็น retained; การ flag ไม่ได้แปลว่าช่วยรักษาได้ |
| Recall | 96.6258% | จับ churn ได้ 315 จาก 326 ราย | พลาด churn น้อย เหมาะกับสมมติฐาน FN แพงกว่า | ต้องแลกกับ 91 FP; ไม่ใช่ retention success rate |
| F1 | 0.860656 | ค่าเฉลี่ยฮาร์มอนิก Precision/Recall | สมดุลพอใช้กับ threshold ที่เน้น recall | ไม่ใช่ objective ที่นำมาเลือก threshold และไม่บอก profit |
| Brier Score | 0.024355 | ค่าเฉลี่ย (probability−label)² | ดีกว่า constant Train-prevalence baseline 0.135017 | คะแนนรวมดีไม่รับประกัน calibration ทุกช่วง |
| Illustrative decision loss | 146 | 5×11 + 91 | ผลต้นทุนผิดพลาดจริงบน Test ภายใต้กติกาที่ตรึงแล้ว | หน่วยสมมติ ไม่ใช่บาท ไม่ใช่ ROI |

| Actual / Action | ไม่ติดต่อ: No Action | Flag เพื่อพิจารณาติดต่อ | รวม |
|---|---:|---:|---:|
| Retained | TN = 1,609 | FP = 91 | 1,700 |
| Churned | FN = 11 | TP = 315 | 326 |
| รวม | 1,620 | 406 | 2,026 |

- **TP 315:** ระบุลูกค้าที่มี label churn ได้ ไม่ได้แปลว่าป้องกัน churn ได้ 315 คน
- **FP 91:** ภายใต้กติกาสอนคือ contact ที่ไม่จำเป็นต่อการจับ churn ใน snapshot; ถ้าทำจริงอาจมีต้นทุน/ผลกระทบประสบการณ์
- **FN 11:** พลาด 3.37% ของ churners ใน Test; โมเดลไม่ครอบคลุมทุกคน
- **TN 1,609:** ตัดสินใจไม่ flag คน retained ได้ถูกต้อง

Flag rate = **406/2,026 = 20.04%**; False-positive rate = **91/1,700 = 5.35%** การติดต่อ 20% ของฐานอาจเกินหรือไม่เกินกำลังทีมก็ได้ เพราะไม่มี capacity จริงในข้อมูล

ตรวจสูตรย้อนกลับ: Precision = 315/406; Recall = 315/326; F1 = 630/732; Accuracy = 1,924/2,026; Loss = 5×11+91 = 146 ทุกค่าตรงกับไฟล์ส่งออก

**ไม่ใช่ผลทดสอบ out-of-time** Test นี้เป็น random stratified holdout ภายใน snapshot เดียวกัน และไม่ได้ให้ causal estimate ของการติดต่อ

## 12. Bootstrap confidence intervals

หลักฐาน: [Cell 35](notebook_cells.txt#L851)–[Cell 36](notebook_cells.txt#L856)

| Metric | Point estimate | 95% CI ต่ำ | 95% CI สูง |
| --- | --- | --- | --- |
| Average Precision | 0.971949 | 0.959576 | 0.981384 |
| ROC-AUC | 0.993049 | 0.989694 | 0.995728 |
| Recall | 0.966258 | 0.945563 | 0.985299 |
| Precision | 0.775862 | 0.740321 | 0.812595 |

ใช้ customer bootstrap แบบสุ่มกลับคืน 500 ครั้ง seed 42 แต่ละครั้ง resample `(label, probability, flag)` ด้วย indices เดียวกัน; model/threshold คงเดิม ตรวจกรณีเหลือเพียง class เดียวก่อน ROC-AUC รอบจริงได้ valid replicates **500/500** Percentiles 2.5% และ 97.5% ถูกต้อง ผู้ตรวจใช้สูตรอิสระคำนวณซ้ำได้ CI เดียวกัน

Intervals นี้ใช้ได้ในฐานะ **conditional sampling uncertainty ของโมเดลและ policy ที่ fit ไว้แล้ว** ไม่ครอบคลุมการเปลี่ยน training sample, เลือก hyperparameters/threshold ใหม่, temporal drift, dataset-selection bias หรือภาวะลูกค้าในครัวเรือนเดียวกันที่ key ปัจจุบันไม่บอก

จำนวน 500 เหมาะกับ enhancement งานวิชา แต่ปลายช่วงยังมี Monte Carlo uncertainty หากต้องใช้ตีพิมพ์หรือเปรียบเทียบความต่างเล็กมาก อาจเพิ่ม resamples และออกแบบ paired comparison ล่วงหน้า การเพิ่มจำนวน bootstrap ไม่แก้ temporal limitation

## 13. Probability calibration: ranking ดี แต่ score ยังคลาดในบางช่วง

หลักฐาน: [Cell 37](notebook_cells.txt#L880)–[Cell 38](notebook_cells.txt#L888)

**Brier = 0.024355** ดีกว่า Train-prevalence constant **0.135017**; ค่าเฉลี่ย predicted probability = **18.3637%**, observed Test churn = **16.0908%** จึง overpredict ค่าเฉลี่ย **2.2729 จุดเปอร์เซ็นต์**

| กลุ่ม quantile ใน Test | n | Mean predicted | Observed churn | คลาดเคลื่อนที่ควรอ่าน |
|---|---:|---:|---:|---|
| คะแนนประมาณ 0.039–0.274 | 203 | 10.74% | 4.93% | Overpredict 5.82 จุดเปอร์เซ็นต์ |
| คะแนนประมาณ 0.274–0.968 | 202 | 70.16% | 55.94% | Overpredict 14.22 จุดเปอร์เซ็นต์ |
| คะแนนประมาณ 0.968–0.999 | 203 | 98.90% | 99.51% | Underpredict 0.61 จุดเปอร์เซ็นต์ |

Bin 0.274–0.968 กว้างมาก ตัวเลข 70.16% กับ 55.94% คือค่าเฉลี่ยใน bin ไม่ใช่หลักฐานว่าลูกค้าทุกคนที่ได้ score 0.70 มีความเสี่ยงจริง 0.5594 และยังไม่บอก calibration เฉพาะรอบ threshold 0.2710 อย่างละเอียด

แปล reliability plot ถูกต้อง: เหนือเส้นทแยงคือ observed > predicted หรือ underprediction; ใต้เส้นคือ overprediction ไม่มีการ fit calibrator บน Test

Brier รวมทั้ง calibration และ discrimination/resolution จึงตีความว่า “Brier ต่ำ แปลว่า calibrated ดีทุกช่วง” ไม่ได้ สอดคล้องกับ [คำอธิบาย calibration ของ scikit-learn](https://scikit-learn.org/stable/modules/calibration.html)

**ใช้ score ทำอะไรได้:** ranking และ threshold ที่ประเมิน empirical error cost บน Validation/Test นี้มีหลักฐานรองรับ แม้ probabilities ไม่สมบูรณ์

**ยังใช้ทำอะไรไม่ได้:** แทนความน่าจะเป็นจริงใน expected CLV/ROI โดยตรง หรืออ้างว่า calibrated พอสำหรับแคมเปญจริง หากพัฒนาต่อ ให้ตรวจ/recalibrate จากข้อมูลฝึกหรือ calibration partition ที่ถูกต้อง แล้วเลือก threshold ใหม่และประเมินบน holdout ใหม่ ห้ามใช้ Test นี้แก้โมเดลแล้วอ้างเป็นผลทดสอบอิสระชุดเดิม

## 14. SHAP global, dependence และ local example

### 14.1 ตรวจความถูกต้องของ implementation

หลักฐาน: [Cell 39](notebook_cells.txt#L908)–[Cell 45](notebook_cells.txt#L1071)

โมเดลที่อธิบายคือ **Random Forest tuned** ไม่ใช่ LightGBM ฟังก์ชันใช้ feature transformer และ ColumnTransformer ที่ fit แล้วของ forest นั้น ไม่ได้เอา preprocessing ของโมเดลอื่นมาปะปน และไม่ fit ซ้ำกับ Test

`forest.classes_ = [0, 1]`, positive class index = **1**, transformed columns = **39** ฟังก์ชันรับ list, ndarray หลายตำแหน่ง class axis และ Explanation แล้วตรวจผลรวมกับ Churn=1 probabilities ก่อนใช้

ผลจริง `tree_path_dependent`, output scale เป็น forest class probability และ **max additivity error = 1.93×10⁻¹⁴** ต่ำกว่า tolerance มาก ไม่พบ wrong class, wrong baseline, double preprocessing หรือชื่อ feature ไม่ตรง matrix

ผู้ตรวจทดสอบ helper เพิ่มด้วย synthetic shape fixtures: list, ndarray ทั้งสาม layout, Explanation แบบหลาย/หนึ่ง class, positive class index 0 และการสลับ class ผิด ผลถูกต้องทุกกรณีที่ทดสอบ การทดสอบนี้ไม่ใช่การรัน SHAP ทุกรุ่นจริง และ fallback แบบ interventional ไม่ถูกเรียกในรอบข้อมูลจริง

แนวทางแยก class axis ตาม output format มีเหตุผล เพราะ SHAP มีการเปลี่ยนรูปแบบ return ของ multi-output ระหว่างเวอร์ชันตาม [เอกสาร TreeExplainer](https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html) Additivity check ยืนยันการประกอบ prediction ใน output scale ที่ใช้ ไม่ใช่การพิสูจน์ causality

### 14.2 Global importance ของ forest

| Source/engineered feature | Mean absolute grouped SHAP |
| --- | --- |
| Total_Trans_Ct | 0.147118 |
| Total_Trans_Amt | 0.091323 |
| Total_Revolving_Bal | 0.062069 |
| Total_Ct_Chng_Q4_Q1 | 0.047645 |
| average_ticket | 0.043360 |
| Avg_Utilization_Ratio | 0.039959 |
| Total_Relationship_Count | 0.030996 |
| contact_ratio | 0.029243 |
| Total_Amt_Chng_Q4_Q1 | 0.019938 |
| Months_Inactive_12_mon | 0.018477 |

ใช้ random Test sample **200 คน** สำหรับ global summaries ไม่ตั้งใจเติมคนคะแนนสูงสุดเข้า sample global; local case ถูกจัดการแยก จึงไม่ทำให้ global importance ลำเอียงจาก deliberate high-risk inclusion

`Total_Trans_Ct` มากสุดจริง ตามด้วย amount, revolving balance, count-change และ average_ticket เป็น **model reliance** ไม่ใช่เปอร์เซ็นต์ความสำคัญรวมกันเป็น 100%, causal contribution, intervention value หรือ profit ranking

การ aggregate dummy ทำโดยรวม signed SHAP ภายใน source field ต่อคนก่อนหา mean absolute; ถูกต้องตามนิยามที่ประกาศและรักษาผลรวมรายคน แต่ค่ารวมอาจหักล้างกันและไม่เท่ากับการคำนวณ Shapley game ใหม่ที่จัด source features เป็นผู้เล่นตั้งแต่ต้น

### 14.3 รูปแบบ Total_Trans_Ct ที่เห็นจริง

ช่วง counts 10–45 ใน sample มี 45 คนและ contributions เป็นบวกทั้งหมด ค่าเฉลี่ยประมาณ **+0.1071**; ช่วง 46–60 มีทั้งบวกและลบ; ช่วง 61–70, 71–81 และ 82–139 มี contributions เป็นลบทั้งหมดใน sample นี้ โดยค่าเฉลี่ยประมาณ **−0.1392, −0.1730, −0.2269** ตามลำดับ

กราฟจึงแสดงการเปลี่ยนทิศในบริเวณประมาณ 50–60 transactions และความเสี่ยงที่ forest ให้ต่ำลงเมื่อ activity สูงขึ้นเทียบ reference ที่ใช้ ตัวเลข band ที่ผู้ตรวจสรุปนี้ใช้บรรยายรูปที่คำนวณแล้ว ไม่ได้นำไปตั้ง threshold หรือเลือกโมเดลใหม่

**ยังสรุปไม่ได้:** จุดหักเป็น universal trigger, เพิ่ม transaction count แล้ว probability จะลดตาม SHAP หรือรูปนี้คงเดิมในอีกช่วงเวลา Vertical spread อาจมาจาก interaction/ตัวแปรสัมพันธ์; tails มี sample น้อย และรูปอธิบาย forest เท่านั้น

### 14.4 ลูกค้าตัวอย่างความเสี่ยงสูงสุดของ forest

เลือกด้วย `argmax(forest_explanation_probability)` จริง ไม่ใช้ observed label ไม่เปิดเผย CLIENTNUM และไม่อ้างว่าเป็นคนที่เสี่ยงสุดของ LightGBM

| Feature ต้นทาง/derived | ค่าของลูกค้าตัวอย่าง | Grouped SHAP ของ forest |
|---|---:|---:|
| Total_Trans_Ct | 42 | +0.159158 |
| Total_Trans_Amt | 2,465 | +0.116532 |
| Total_Ct_Chng_Q4_Q1 | 0.355 | +0.060836 |
| Total_Revolving_Bal | 0 | +0.055091 |
| contact_ratio | 1.5 | +0.034208 |
| Avg_Utilization_Ratio | 0 | +0.033892 |
| Total_Relationship_Count | 2 | +0.031973 |
| Credit_Limit | 2,145 | −0.007323 |
| Avg_Open_To_Buy | 2,145 | −0.007299 |
| average_ticket | 2,465/42 ≈ 58.69 | −0.006049 |

ผลรวมครบทุก feature ไม่ใช่เฉพาะรายการในตาราง:

**reference 0.4988689535 + contributions 0.4987035072 = probability 0.9975724607**

Reference ประมาณ 0.499 เป็น baseline ภายใน attribution ของ weighted forest ไม่ใช่ churn prevalence จริงประมาณ 0.161 การอ่านค่า reference เป็น base rate ประชากรจะผิด

ปริมาณธุรกรรมต่ำ, count-change ต่ำ, revolving/utilization ศูนย์ และ relationship depth ต่ำเป็นหลักฐานที่ forest ใช้เพิ่ม score ของคนนี้ ปัจจัยบางตัวช่วยลด score เล็กน้อย แต่รวมแล้ว forest ให้ค่าสูงมาก ไม่มีส่วนใดยืนยันว่าปัจจัยเหล่านี้ทำให้ลูกค้า churn หรือการแก้ปัจจัยใดจะช่วยรักษาได้

## 15. Subgroup diagnostics

หลักฐาน: [Cell 47](notebook_cells.txt#L1130)–[Cell 48](notebook_cells.txt#L1136); ใช้ final LightGBM predictions ที่ตรึงแล้ว ไม่ใช่ forest probabilities ในส่วน SHAP

| กลุ่มตัวอย่าง | n | Churn prevalence | Recall | Precision | Brier |
|---|---:|---:|---:|---:|---:|
| Gender F | 1,039 | 17.61% | 98.36% | 84.91% | 0.017153 |
| Gender M | 987 | 14.49% | 94.41% | 69.59% | 0.031936 |
| Income $60K–$80K | 282 | 9.57% | 96.30% | 52.00% | 0.039136 |
| Income Less than $40K | 674 | 17.21% | 97.41% | 83.70% | 0.020261 |

มี 19 subgroup slices ผ่านเกณฑ์แสดง Precision/Recall 14 slices และ suppress 5 slices ตาม n/จำนวน class/จำนวน flags ที่ประกาศ เช่น Gold n=20, Platinum n=4, Silver มี churn เพียง 19 คน; Doctorate n=98; Post-Graduate มี churn 19 คน

ผลแสดงว่า Precision และ Brier แตกต่างกันพอควรในบางกลุ่ม โดยเฉพาะกลุ่มรายได้ $60K–$80K ซึ่งมี base rate ต่ำกว่า การแปลผลต้องแยกผลของ prevalence, customer mix และข้อผิดพลาดโมเดล ไม่ใช่ประกาศว่าโมเดล “เป็นธรรม” หรือ “เลือกปฏิบัติ” จาก point estimates เหล่านี้เพียงอย่างเดียว

ช่วง Recall ของ slices ที่ผ่านเกณฑ์คือ **92.59%–100%** แต่หลาย slice มีลูกค้าคนเดียวกันซ้ำข้ามมิติ จึงไม่ใช่ independent comparisons และยังไม่มี subgroup confidence intervals/multiplicity adjustment ผลนี้เหมาะสำหรับชี้จุดตรวจต่อ ไม่ใช้เปลี่ยน threshold รายกลุ่มจาก Test ปัจจุบัน

## 16. Business interpretation, survival, uplift และการทดลอง

หลักฐาน: [Cell 2](notebook_cells.txt#L71), [Cell 49](notebook_cells.txt#L1161)–[Cell 52](notebook_cells.txt#L1253), [Cell 57](notebook_cells.txt#L1328)

### 16.1 แยกหลักฐานสามระดับ

| ระดับ | สิ่งที่พูดได้ |
|---|---|
| A. ข้อมูล/โมเดลแสดงจริง | Behavioral activity แยก observed attrition ได้มาก; LightGBM จัดอันดับและจับ churn ใน held-out snapshot ได้ดี; forest ใช้ transaction-related variables มากใน SHAP |
| B. ธุรกิจอาจทดสอบ | Engagement/reactivation review สำหรับ activity ต่ำ; service check เมื่อมี inactivity ตามเงื่อนไขที่ตรวจบริบทแล้ว; ตรวจ service friction เมื่อ contacts สูง; relationship-needs review เมื่อความสัมพันธ์ตื้น |
| C. ต้องมีหลักฐานทดลอง | ใครถูกช่วยให้อยู่ต่อเพราะการติดต่อ, treatment ใดได้ผล, incremental retained margin, ความคุ้มค่าและผลเสียต่อบางกลุ่ม |

Notebook ไม่แปลง correlation หรือ positive SHAP เป็น treatment effect และไม่สร้าง CLV รายคนขึ้นเอง การใช้ Risk × CLV ถูกระบุว่าเป็นกรอบแนวคิด ไม่ใช่ CLV segmentation ที่คำนวณจาก dataset นี้

สูตร `P(churn) × P(save|action) × CLV − cost` เป็น shorthand ที่ต้องตีความ `save` ว่า rescue ที่เพิ่มขึ้นเพราะ treatment ในกลุ่มที่จะ churn หากไม่ทำอะไร ไม่ใช่ stay rate ของคนที่ถูกติดต่อทั้งหมด หากมีผลเสียจากการติดต่อด้วย ต้องพิจารณา net uplift ที่รวมทั้งผลช่วยและผลเสีย Notebook ให้สูตร uplift-based value และอธิบาย Sleeping Dogs ต่อ จึงไม่มี empirical ROI ที่คำนวณผิด แต่เวลานำสูตรแรกไปใช้จริงควรระบุ conditioning/สมมติฐานให้ครบ

### 16.2 Survival และ causal uplift

ไม่พบการ fit Kaplan–Meier, Cox, survival forest หรือ hazard จาก `Months_on_book` อย่างผิดวิธี มีการระบุว่าต้องมี observation origin, event date และ censoring date ก่อน ประโยคว่า empirical survival ไม่ identified จาก snapshot นี้ถูกต้อง

Uplift ใช้ outcome **Y=1 คือ retained** ขณะที่ classifier ใช้ **Churn=1** การสลับ sign convention ถูกอธิบายไว้; `p1(x)−p0(x)` จึงหมายถึงเพิ่มโอกาสอยู่ต่อ ไม่ใช่เพิ่ม churn ไม่มีการ fit uplift model จากข้อมูลที่ไม่มี treatment/control และการแบ่ง Persuadables/Sure Things/Lost Causes/Sleeping Dogs เป็นแนวคิด ไม่ได้อ้างว่าระบุประเภทแต่ละคนได้จริง

### 16.3 ประเมินแผน A/B test

| องค์ประกอบ | มีหรือไม่ | ผลประเมิน |
|---|---|---|
| Eligible population | มี | ระบุ high-risk cohort และ account/contact eligibility ที่ต้องกำหนดล่วงหน้า |
| Treatment / control | มี | Intervention เทียบ business as usual; ต้องกำหนดข้อความ/ช่องทาง/ข้อเสนอจริงก่อน launch |
| Outcome / horizon | มีเป็นข้อกำหนด | Retained ณ horizon H ที่ต้องประกาศ; ไม่สร้าง H จากข้อมูลที่ไม่มี |
| Randomization | มี | Customer-level, พิจารณา risk stratification และ cluster/spillover |
| Sample size / power | มีเป็นแผน | ต้องหา control retention, MDE, alpha, power และ clustering ก่อนคำนวณ; ไม่แต่ง sample size |
| Exclusions | มี | กำหนดก่อน randomization; ไม่ตัดคนไม่ตอบสนองออกทีหลัง |
| Analysis | มี | Intention-to-treat รวม non-delivery และรายงาน CI |
| Stop rule | มี | Fixed horizon หรือ preregistered sequential boundaries; ไม่แอบดูแล้วหยุดตาม p-value |
| Cost / margin | มี | วัด contact, incentive, service และ incremental contribution margin ใน horizon เดียวกัน |
| Guardrails | มี | Complaints, opt-outs, adverse outcomes และ fairness/safety |

แผนเหมาะเป็น **กรอบออกแบบการทดลอง** ยังไม่ใช่ protocol พร้อม launch เพราะ treatment จริง, H, MDE และ sample size ยังต้องกำหนด การไม่เดาตัวเลขเหล่านี้เป็นความถูกต้อง ไม่ใช่ช่องว่างที่ควรเติมด้วยเลขสมมติแล้วอ้างว่าเป็นข้อค้นพบ

ตัวชี้วัดธุรกิจหลักต้องเป็น retention lift พร้อม CI และ incremental net margin หลังหักต้นทุนทั้งหมด ไม่ใช่ AP หรือจำนวน TP เพียงอย่างเดียว โมเดลอาจหา Lost Causes ได้แม่นมากแต่รักษาไม่ได้สักคน; นี่เป็นเหตุผลที่ risk ≠ treatment effectiveness

### 16.4 Monitoring และ deployment

ครอบคลุม Data (missingness/drift/category shifts/coverage), Model (AP, precision/recall, calibration, subgroup stability), Business (randomized lift, contact rate, margin/net value), Operations (latency/capacity/eligibility/fairness/safety) ครบ

คำอธิบาย concept drift ว่า `P(Y|X)` เปลี่ยนแม้โค้ดเดิมถูกต้อง; input drift ไม่ได้พิสูจน์ concept drift และ PSI/distribution tests ไม่ใช่คำสั่ง retrain อัตโนมัติ มีการรอ labels mature และพิจารณาผลของ campaign ต่อ labels ด้วย

ข้อ stop-loss ที่อิง harmful uplift, negative net value, guardrail failure หรือ drift เกินขอบเขตใช้ได้ในเชิงแนวคิด และมีคำเตือนเรื่อง uncertainty/sequential rules ไม่ควรใช้ Notebook นี้เปิด campaign จริงทันทีแม้รันผ่าน

## 17. ตรวจไฟล์ส่งออกและความสอดคล้อง

หลักฐาน: [Cell 30](notebook_cells.txt#L705), [Cell 32](notebook_cells.txt#L753), [Cell 34](notebook_cells.txt#L818), [Cell 36](notebook_cells.txt#L856), [Cell 41](notebook_cells.txt#L1016), [Cell 48](notebook_cells.txt#L1136), [Cell 54](notebook_cells.txt#L1278) และ [ตารางตรวจ CSV](output_file_checks.csv)

| ไฟล์ | แถว | Missing cells | แถวซ้ำ | คำอธิบาย |
| --- | --- | --- | --- | --- |
| calibration_bins.csv | 10 | 0 | 0 | 10 quantile bins; ค่าตรงกับ predictions |
| cv_results.csv | 12 | 4 | 0 | missing 4 จุดคือ max_depth=None; คอลัมน์เวลารันเปลี่ยนได้ |
| data_dictionary.csv | 23 | 0 | 0 | ครอบคลุม source fields 23 ตัว; หน่วย/ช่วงที่ไม่ทราบระบุไว้ |
| final_metrics.csv | 14 | 20 | 0 | missing 20 จุดคือ CI ที่ไม่ได้คำนวณให้ 10 metrics; ไม่ใช่ missing labels |
| model_comparison.csv | 7 | 3 | 0 | missing 3 จุดคือ CV ROC-AUC/Recall/F1 ของ tuned RF ที่ search ใช้ AP อย่างเดียว |
| partition_summary.csv | 3 | 0 | 0 | n และ prevalence ตรงกับ split ที่คำนวณใหม่ |
| retention_hypotheses.csv | 4 | 0 | 0 | 4 สมมติฐานตาม observed training endpoints; ไม่ใช่ treatment estimates |
| shap_global_importance.csv | 39 | 0 | 0 | 39 transformed features ของ Random Forest |
| shap_source_importance.csv | 21 | 0 | 0 | 21 source/engineered fields; signed aggregation ก่อน absolute mean |
| subgroup_metrics.csv | 19 | 10 | 0 | missing 10 จุดคือ Precision/Recall ของ 5 slices ที่ตัวอย่างไม่พอ |
| test_predictions.csv | 2026 | 0 | 1 | 2,026 คน; มีคู่ผลเหมือนกัน 1 คู่ แต่เป็นคนละ CLIENTNUM และคนละ profile |
| validation_threshold_analysis.csv | 2028 | 0 | 0 | ตรวจใหม่ทุก 2,028 แถว; confusion counts และ cost ตรงทั้งหมด |

**แถว predictions ที่เหมือนกันไม่ใช่ลูกค้าซ้ำ:** ผู้ตรวจย้อนกลับไปยัง split/source ตรวจแล้วเป็นลูกค้าคนละรายและ feature profiles ต่างกัน แต่ LightGBM ให้ probability เดียวกันและมี label/flag เท่ากัน จึงไม่ควร `drop_duplicates()` จาก export สามคอลัมน์นี้ เพราะจะลดจำนวนลูกค้าจริงผิด

`test_predictions.csv` ไม่มี CLIENTNUM/identifier, ไม่มี missing labels/probabilities/flags และ flags ตรงกับ `probability >= frozen_threshold` ทุกคน Blank metrics ที่อธิบายด้านบนไม่ควรถูกเติมเป็นศูนย์ เพราะจะเปลี่ยนความหมายเป็นผลที่คำนวณแล้ว

ผลฝังในต้นฉบับมี `TqdmWarning: IProgress not found` เกี่ยวกับ widget ใน cell import ไม่ใช่ model error; รอบ audit ใหม่ไม่มี warning ดังกล่าว ไม่พบ deprecated API warning, convergence warning หรือ shape warning ในการรันจริงครั้งนี้

มี 17 PNG figures และ CSV ครบ 12 ไฟล์ ส่วน `frozen_policy.json` และ `run_manifest.json` ช่วยบันทึก threshold, final model, course forest, source checksum, versions และ SHAP reference แต่หากแจกเฉพาะ SHAP CSV ควรพ่วง metadata ชื่อโมเดลให้ชัด

## 18. สิ่งที่ข้อมูลนี้ยังตอบไม่ได้

1. **Future predictive stability:** ไม่ทราบ t0, cutoff และ future label horizon จึงไม่รู้ว่า features ใช้ได้ ณ scoring date จริงหรือไม่
2. **Causality:** ความสัมพันธ์จาก EDA, coefficients และ SHAP ไม่ใช่ผลของการแทรกแซง
3. **Intervention effectiveness:** ไม่มี treatment/control และ post-treatment outcomes ว่า contact/incentive ช่วยเพิ่ม retention หรือไม่
4. **Customer-level uplift:** ระบุ persuadable customers จาก snapshot นี้ไม่ได้
5. **Survival timing:** ไม่มี event/censoring timeline ที่ใช้ประมาณเมื่อใดจะ churn ได้
6. **CLV และ ROI จริง:** ขาด validated CLV/contribution margin, intervention success และต้นทุนครบถ้วน
7. **Population representativeness:** ไม่รู้ว่าการคัดเลือกข้อมูลนี้แทนลูกค้าปัจจุบันของบริษัทใดเพียงใด
8. **Fairness หรือความปลอดภัยสำหรับใช้งานจริง:** subgroup point metrics ไม่ใช่การรับรอง; ต้องมีบริบทและ guardrails ของการใช้งานจริง

Notebook ยอมรับข้อจำกัดเหล่านี้ตั้งแต่ต้นและย้ำท้ายงานอย่างสม่ำเสมอ ไม่พบการ fit survival/uplift ปลอม หรืออ้างว่า AP สูงยืนยัน retention ROI

## 19. บันทึกตรวจครบทุก cell

ตารางนี้รวมทุก Markdown/code cell ของต้นฉบับ ตัวแปรที่ใช้ใน code cells มีการกำหนดก่อนเรียกในลำดับที่รันจริง ไม่มี NameError, syntax error, shape mismatch หรือ hidden state ที่ต้องพึ่งการรันนอกลำดับในเส้นทางที่ทดสอบ

| Cell | ชนิด | หน้าที่ | ผลตรวจลำดับ/inputs/ข้อสังเกต |
| --- | --- | --- | --- |
| [Cell 1](notebook_cells.txt#L2) | Markdown | วางขอบเขต/agenda/architecture | ข้อความ snapshot และ provenance ถูก; แผนภาพควรย้าย split ก่อน EDA |
| [Cell 2](notebook_cells.txt#L71) | Markdown | นิยาม churn และ economic framework | แยก concept/empirical evidence; ไม่แต่ง CLV/ROI; สูตร rescue ต้องอ่านตามเงื่อนไข |
| [Cell 3](notebook_cells.txt#L102) | Code | Imports, constants, paths, display helpers | เป็นจุดเริ่มครบ; seeds 42, warning ไม่ถูก suppress ทั้งหมด; รันผ่าน |
| [Cell 4](notebook_cells.txt#L176) | Markdown | อธิบาย discovery และ integrity | อยู่ก่อนโหลดข้อมูลและระบุข้อจำกัดถูกต้อง |
| [Cell 5](notebook_cells.txt#L184) | Code | หา CSV ตาม target, validate labels, schema พื้นฐาน | ใช้ INPUT_ROOT จาก cell 3; รันผ่าน; ควรเพิ่ม required predictor checks ที่นี่ |
| [Cell 6](notebook_cells.txt#L222) | Code | Data dictionary | ใช้ raw ที่โหลดแล้ว; ระบุหน่วย/ช่วงที่ไม่ทราบ; export ครบ 23 fields |
| [Cell 7](notebook_cells.txt#L257) | Code | Missing/ranges/inf/duplicates, target mapping | raw/field_info พร้อม; mapping ตรวจ labels ก่อนแล้ว; ไม่ลบคน profile เหมือนกัน |
| [Cell 8](notebook_cells.txt#L303) | Markdown | ความหมาย majority baseline | แยก snapshot prevalence จาก churn rate แบบมีช่วงเวลา |
| [Cell 9](notebook_cells.txt#L309) | Code | Counts/prevalence และเทียบ course reference | ใช้ data/Churn ที่นิยามแล้ว; ค่าจริงไม่ถูก hardcode |
| [Cell 10](notebook_cells.txt#L332) | Markdown | Predeclared split/model policy | กำหนด roles และ tolerance ก่อน CV/Validation/Test; family selection บน Validation มี Test แยก |
| [Cell 11](notebook_cells.txt#L346) | Code | Stratified split 60/20/20 และ key overlap | ก่อน fitted preprocessing/EDA; random seed และ pairwise disjointness ถูกต้อง |
| [Cell 12](notebook_cells.txt#L364) | Markdown | Training-only EDA และ Wilson CI | แยก observational association กับ causation และ small-n caution |
| [Cell 13](notebook_cells.txt#L371) | Code | Segment functions และ activity/inactivity/depth EDA | ใช้ train; qcut ไม่ได้ใช้ Test; function inputs พร้อม; required schema check อยู่ช้า |
| [Cell 14](notebook_cells.txt#L404) | Code | Numeric/categorical plots และ correlation | ใช้ train; label ไม่ปะปนเข้า numeric predictor matrix; ไม่ fit estimator |
| [Cell 15](notebook_cells.txt#L447) | Markdown | Cross-tab sparsity/multiple testing | ไม่ทำ chi-square ที่คาดหวังต่ำ; อธิบายข้อจำกัด multivariate ML ถูกต้อง |
| [Cell 16](notebook_cells.txt#L451) | Markdown | Leakage สี่ประเภท | แยก temporal limitation; ย้ายก่อน EDA ได้เพื่อให้เส้นเรื่องชัด |
| [Cell 17](notebook_cells.txt#L465) | Code | Exclude ID/target/NB, whitelist, build X/y | ก่อน modeling ถูกต้อง; ใช้ data/train indices ที่นิยามแล้ว; schema checks ควรเร็วกว่านี้ |
| [Cell 18](notebook_cells.txt#L491) | Markdown | อธิบาย ratio features | safe denominator และขอบเขต temporal มีครบ; ไม่เรียก derived ratios ว่า causal |
| [Cell 19](notebook_cells.txt#L503) | Code | Reusable row-local feature function และ column types | ใช้ X_train; input ไม่ถูกแก้; no new NaN/inf; correlations เป็น Train เท่านั้น |
| [Cell 20](notebook_cells.txt#L531) | Markdown | RFM/rolling/event architecture แนวคิด | ไม่สร้างเวลา/rolling data จาก snapshot ปลอม |
| [Cell 21](notebook_cells.txt#L551) | Markdown | Preprocessing rationale | scaler สำหรับ tree ไม่จำเป็นแต่ใช้ร่วมกับ linear baseline ได้; unseen-category warning เชิง monitoring ถูก |
| [Cell 22](notebook_cells.txt#L559) | Code | ColumnTransformer/Pipeline/CV folds | ไม่มี fit ก่อน CV; clone ภายใน estimator; encoder API branch เหมาะสม |
| [Cell 23](notebook_cells.txt#L586) | Markdown | Baselines และ logistic/RF concepts | progression มีเหตุผล; AP ต่างจาก accuracy; ระบุ odds ไม่ใช่ probabilities |
| [Cell 24](notebook_cells.txt#L599) | Markdown | Class weighting / oversampling | SMOTE/ADASYN อยู่เชิงแนวคิด; resampling-fold rule ถูกต้อง |
| [Cell 25](notebook_cells.txt#L608) | Code | CV baselines, optional boosters และ fit Train | ใช้ cv_splits/X_train/y_train; ไม่แตะ Validation/Test; รันครบทุกโมเดลใน environment นี้ |
| [Cell 26](notebook_cells.txt#L655) | Markdown | Benchmark caveats | เปิดเผย objective/weighting ต่างกัน; ไม่อ้างว่าเป็น controlled test ของ weighting |
| [Cell 27](notebook_cells.txt#L659) | Markdown | RF grid และ overfitting interpretation | กำหนด AP และ Train-only tuning ก่อน search |
| [Cell 28](notebook_cells.txt#L667) | Code | GridSearchCV และเลือก forest variant | 12 configs/3 folds; preprocessor อยู่ Pipeline; results มาจาก Train; ไม่มี test selection |
| [Cell 29](notebook_cells.txt#L699) | Markdown | Validation model comparison/odds interpretation | รับรู้ validation reuse; ratios/one-hot/regularization จำกัดความหมาย coefficient |
| [Cell 30](notebook_cells.txt#L705) | Code | Candidate Validation probabilities และเลือก final family | classes_ ตรวจ positive=1; AP/Brier tolerance ตาม cell 10; final LightGBM; ไม่คำนวณ Test |
| [Cell 31](notebook_cells.txt#L742) | Markdown | PR/AP และ illustrative threshold costs | อธิบาย AP ไม่เท่ากับ trapezoidal area; no-flags precision convention ระบุไว้ |
| [Cell 32](notebook_cells.txt#L753) | Code | Ranking plots, every-score thresholds, frozen policy | ใช้ Validation เท่านั้น; ทุก 2,028 rows ตรวจซ้ำตรง; threshold/cost ขั้นต่ำจริง |
| [Cell 33](notebook_cells.txt#L799) | Markdown | Frozen Test metrics business interpretation | แปล TP/FP/FN/TN อย่างไม่อ้างว่าสามารถ rescue ลูกค้าได้จริง |
| [Cell 34](notebook_cells.txt#L818) | Code | Final model Test probabilities/metrics/predictions | model+threshold ตรึงแล้ว; count/metrics/flags ตรงกัน; export ไม่มี identifier |
| [Cell 35](notebook_cells.txt#L851) | Markdown | Bootstrap scope | อธิบาย conditional uncertainty และข้อจำกัดครบ |
| [Cell 36](notebook_cells.txt#L856) | Code | 500 bootstraps และ final_metrics export | resample indices ร่วมกัน; single-class guard ถูก; CI ตรวจซ้ำตรง; ไม่ fit โมเดล |
| [Cell 37](notebook_cells.txt#L880) | Markdown | Calibration interpretation | อธิบายแนวทแยงและ Brier ถูก; ห้าม fit calibrator บน Test |
| [Cell 38](notebook_cells.txt#L888) | Code | Reliability/Brier/baseline และ mean gap | ใช้ probabilities เดิม; baseline prevalence มาจาก Train; local mismatch ควรชี้เพิ่มใน summary |
| [Cell 39](notebook_cells.txt#L908) | Markdown | SHAP theory และ model/reference distinction | ระบุ forest แยก LightGBM ชัด; ไม่มี causal/profit interpretation |
| [Cell 40](notebook_cells.txt#L924) | Code | Transform forest sample, TreeSHAP และ class resolver | ใช้ fitted forest preprocessor; local เลือก score-only; positive class/additivity ผ่าน |
| [Cell 41](notebook_cells.txt#L1016) | Code | Transformed/source importance และ beeswarm | mapping จาก encoder.categories_ ถูก; global random sample ไม่ถูก high-risk oversample |
| [Cell 42](notebook_cells.txt#L1050) | Markdown | ข้อจำกัด dependence plot | ไม่เปลี่ยน visual bend เป็น threshold production |
| [Cell 43](notebook_cells.txt#L1055) | Code | Total_Trans_Ct dependence scatter | original counts จับคู่ contribution ถูก; sample ordering ตรงกัน |
| [Cell 44](notebook_cells.txt#L1065) | Markdown | Local explanation scope | ระบุ highest forest risk ไม่ใช่ highest final LightGBM risk; ไม่เลือกด้วย label |
| [Cell 45](notebook_cells.txt#L1071) | Code | Local table/grouped waterfall | ค่าต้นทาง/derived ตรง; base+sum=forest probability; ไม่มี CLIENTNUM |
| [Cell 46](notebook_cells.txt#L1114) | Markdown | Explanation boundaries | correlated inputs/derived features/reference/causality กล่าวถูกต้อง |
| [Cell 47](notebook_cells.txt#L1130) | Markdown | Subgroup criteria | กำหนด minimum counts; audit ไม่ใช่ protected-class causal claim |
| [Cell 48](notebook_cells.txt#L1136) | Code | Subgroup diagnostics/export | กลับมาใช้ final Test probabilities ไม่ใช้ forest; suppress P/R เมื่อข้อมูลน้อย; ไม่ปรับ policy |
| [Cell 49](notebook_cells.txt#L1161) | Markdown | Retention playbook flow | risk-ranked review ตามด้วย randomized pilot; ไม่ข้ามไปอ้างผลรักษาลูกค้า |
| [Cell 50](notebook_cells.txt#L1183) | Code | สร้าง hypothesis table จาก Train EDA | inputs มาจาก train segments; endpoint counts ผ่านเกณฑ์; ข้อสรุป inactivity ควรอ่านรูปแบบเต็ม |
| [Cell 51](notebook_cells.txt#L1209) | Markdown | Survival/uplift/experiment | ไม่มี empirical survival/uplift fit; outcome sign convention และ ITT/preregistration ถูกต้อง |
| [Cell 52](notebook_cells.txt#L1253) | Markdown | Monitoring/deployment | ครอบคลุม 4 ด้าน; concept drift/label maturity/stop-loss มีข้อจำกัดชัด |
| [Cell 53](notebook_cells.txt#L1273) | Markdown | Export verification scope | ระบุ assertions ตรวจ mechanical contracts ไม่ใช่ causality |
| [Cell 54](notebook_cells.txt#L1278) | Code | Export, manifest, consistency assertions | ตัวแปรจากขั้นก่อนครบ; CSV/figures จริง; file existence ไม่แทน independent recalculation ซึ่งผู้ตรวจเพิ่มแล้ว |
| [Cell 55](notebook_cells.txt#L1302) | Markdown | Quality checklist | เป็น checklist แบบข้อความ; รอบ audit ยืนยันแกนหลักจริง; ไม่ตีความว่าได้ทดสอบทุกเวอร์ชัน |
| [Cell 56](notebook_cells.txt#L1324) | Markdown | เปิด executive summary | อยู่ท้ายงานถูกต้อง; ระบุว่าจะใช้ผลคำนวณจริง |
| [Cell 57](notebook_cells.txt#L1328) | Code | Dynamic executive summary | model names/EDA/metrics/SHAP มาจากตัวแปรจริง; แยก observed/hypothesis/causal evidence; ควรชี้ local calibration เพิ่ม |

ตัวแปรสำคัญไม่ถูกเขียนทับข้ามบทบาทโดยไม่ชัดเจน: `final_model` เป็น LightGBM, `course_forest_pipeline` แยกไว้, `test_probability` คงเป็น final model, `forest_explanation_probability` ใช้เฉพาะ SHAP; `validation_probability` ไม่ถูกแทนด้วย Test การเติม `Transaction_quartile` ลง `train` ไม่หลุดเข้า predictors เพราะ X สร้างจาก `data[predictor_columns]`

`resolve_positive_shap` อ้าง shape/class globals ของ sample ที่สร้างไว้ก่อน เป็น dependency ที่เห็นได้และรันตามลำดับได้ ไม่ใช่ hidden state จากเซลล์ที่หายไป แต่ถ้านำฟังก์ชันไปใช้ใน library แยกควรส่ง shape/classes เป็น arguments ให้ชัด ข้อนี้ไม่จำเป็นต้อง refactor สำหรับ Notebook ปัจจุบัน

## 20. หลักฐานประกอบรายงาน

- [ผลรันและ checksum ต้นฉบับ](execution_verification.json)
- [ผลคำนวณ metrics/threshold/bootstrap อย่างอิสระ](independent_verification.json)
- [ตารางค่าที่คำนวณซ้ำเทียบ Notebook](independent_metric_checks.csv)
- [ผลตรวจ CSV ทุกไฟล์](output_file_checks.csv)
- [ผลทดสอบ SHAP output shapes และ safe division](compatibility_checks.json)
- [หลักฐานลำดับ schema check](schema_order_check.json)
- [ข้อความ source ทุก cell สำหรับติดตามตำแหน่ง](notebook_cells.txt)
- [สำเนาที่รันเพื่อ audit โดยปรับเฉพาะ paths และเพิ่ม cell ส่งออกหลักฐาน](runtime/audit_execution.ipynb)

ข้อมูลผลรันใหม่อยู่ใต้ `audit/runtime/kaggle/working/`; ผลตรวจเพิ่มเติมอยู่ `audit/runtime/audit_exports/` ต้นฉบับใน Downloads ไม่ถูกแก้ไข ไม่ได้สร้าง replacement Notebook และไม่ดำเนินการทดลอง retention จริง

เอกสารอ้างอิงภายนอกใช้ตรวจนิยาม/พฤติกรรม API ไม่ใช้แทนหลักฐานการรัน: [แหล่ง dataset Kaggle](https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers/data), [scikit-learn calibration](https://scikit-learn.org/stable/modules/calibration.html), [SHAP TreeExplainer](https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html)

## 21. คำตัดสินสุดท้าย

คะแนนเป็นดุลยพินิจของผู้ตรวจสำหรับ **งานวิเคราะห์ snapshot ในมหาวิทยาลัย** ไม่ใช่ความน่าจะเป็นว่าระบบ production ปลอดภัยหรือรับรองผลกำไร

### A. ความถูกต้องของ Code — 9.5/10

รันครบ 26 code cells ใน kernel ใหม่และคำนวณ outputs ซ้ำตรง; Pipeline/class handling/shape ใช้งานได้ หักจาก required-schema check ที่อยู่หลังเริ่มใช้ fields และ dependency ของ helpers ที่ยังผูกกับ global notebook state

### B. ความถูกต้องของ Statistical / ML Methodology — 9.0/10

แยก Train/Validation/Test ถูก, EDA ใช้ Train, class weighting/CV/AP เหมาะสม, ไม่แต่ง temporal/causal evidence ยังมีการเปรียบเทียบโมเดลแบบ practical recipes และ uncertainty ที่ไม่ครอบคลุม model/threshold selection ทั้งกระบวนการ ซึ่ง Notebook ส่วนใหญ่ระบุไว้แล้ว

### C. Leakage Control — 9.5/10

ตัด source classifier outputs/target/ID, fold-specific preprocessing และ customer disjointness ตรวจผ่าน คะแนนนี้ครอบคลุมการควบคุมที่ทำได้ในโค้ด **ไม่ใช่รับรองว่าไม่มี temporal leakage** เพราะ source ไม่มี timestamps เพียงพอ

### D. Model Evaluation — 9.0/10

Threshold ใช้ Validation และต่ำสุดจริง; Test confusion/metrics/CI/calibration สอดคล้องกัน ไม่มี retuning หลัง Test ควรย้ำ local calibration mismatch และไม่ตีความ CV leader ว่าเหนือกว่าอย่างมีนัยสำคัญจาก point estimates

### E. Business Interpretation — 9.0/10

แยก risk, value, hypothesis, causal experiment และ monitoring ได้ครบ ไม่อ้าง ROI จาก classifier ควรทำประเด็น calibration และ conditional rescue probability ให้ชัดขึ้นในบทสรุปที่ผู้อ่านธุรกิจใช้ตัดสินใจ

### F. Reproducibility / Kaggle Readiness — 9.0/10

JSON/schema/syntax ผ่าน; paths รองรับ Kaggle, seeds/source checksum/versions/exports มีครบ และผลเดิมทำซ้ำได้ ยังไม่ได้รันบน Kaggle infrastructure จริง และไม่ได้ทดสอบทุกเวอร์ชัน/ทุก optional fallback branch จึงไม่ให้เต็ม

### G. Overall — 9.2/10

**จัดประเภท: 2. พร้อมใช้ แต่ควรแก้บางจุดก่อนส่ง**

เหมาะใช้เป็นงาน Business Data Analytics ที่จำแนก historical snapshot และเสนอ retention experiment ผล ranking/classification เชื่อถือได้ภายใต้ protocol ที่ตรวจนี้ แต่ยังไม่ใช่หลักฐาน future forecasting หรือการรักษาลูกค้าอย่างมีกำไร

### สิ่งที่ควรแก้ก่อนเป็นลำดับแรก

1. **เพิ่มคำอธิบาย calibration ที่สำคัญใน executive summary:** กลุ่ม n=202 มี predicted mean 70.16% แต่ observed churn 55.94%; แยกความเหมาะสมของ ranking/empirical threshold ออกจากการใช้ probability คำนวณมูลค่าจริง
2. **ย้าย required-feature schema/type checks มาก่อน EDA:** ให้ source เปลี่ยนแล้วหยุดด้วยข้อความชัดเจน ก่อนเข้าถึง field ที่อาจหายไป
3. **แก้ architecture diagram ให้ split อยู่ก่อน training-only EDA:** ให้ภาพกับโค้ดสอนลำดับเดียวกัน
