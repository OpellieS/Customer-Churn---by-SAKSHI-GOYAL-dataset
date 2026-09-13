# Final publication audit — 2026-09-13

ผล: ไม่พบ CRITICAL/MAJOR และแก้ MINOR ที่ดำเนินการได้ครบแล้ว พร้อมเผยแพร่ภายใต้ข้อจำกัดของ historical snapshot

## การแก้ไข

1. ย้ายการตรวจ schema ที่จำเป็นให้เกิดก่อน EDA พร้อมทดสอบ missing feature และชนิดข้อมูลผิด โดยไม่เปลี่ยนข้อมูลหรือผลโมเดล
2. แก้ process-flow diagram ให้ split มาก่อน training-only EDA ตรงกับโค้ดจริง
3. เพิ่มคำอธิบาย calibration ในบทวิเคราะห์และ executive summary: bin ที่คลาดเคลื่อนมากที่สุด n=202, mean score 70.16%, observed churn 55.94%; ไม่ใช่ค่าความน่าจะเป็นรายจุดหรือหลักฐาน ROI
4. เพิ่มชื่อโมเดล/class/output scale/reference/source hash ใน SHAP CSV เพื่อป้องกันการนำ RF SHAP ไปอธิบาย LightGBM
5. เพิ่ม README, เอกสาร provenance/environment, portable verification scripts และหลักฐานตรวจรอบสุดท้าย; เก็บ audit เดิมโดยระบุว่าเป็นประวัติ

## Execution และ output consistency

Fresh local CPU kernel ผ่าน 57 เซลล์ รวม code 26 เซลล์ และ inspection เพิ่ม 1 เซลล์; ใช้เวลา 23.13 วินาที ไม่พบ warning ภายใน notebook เปลี่ยนเฉพาะ path constants ใน temporary replay; notebook เผยแพร่ยังใช้ Kaggle absolute paths ไม่ได้ทดสอบบน hosted Kaggle โดยตรง

ตรวจ notebook JSON/schema และ Python AST ผ่าน ไม่มี hidden-state failure จากการรันตามลำดับ ผลลัพธ์ทั้ง 31 ไฟล์ถูกสร้างใหม่และค่าตัวเลขเดิมตรงกันทุก analytical CSV (ไม่นับเวลา runtime และ metadata ที่เพิ่ม) ดู [execution.json](execution.json) และ [historical_output_comparison.csv](historical_output_comparison.csv)

## Methodology

Target Attrited Customer=1; ตัด ID และ Naive Bayes leakage columns ทั้งสอง แบ่ง stratified 6,076/2,025/2,026 ด้วย seed42; ไม่มี customer ID ซ้ำข้ามชุด EDA ใช้ train; fitted preprocessing อยู่ภายใน CV; CV/search ใช้ train เท่านั้น การเลือกโมเดลและ threshold ใช้ validation ก่อน frozen test ไม่ fit calibration บน test

## Independent metrics

คำนวณ AP ด้วย precision-recall grouping และ ROC-AUC ด้วย rank/Mann–Whitney จาก predictions; คำนวณ confusion matrix และ metrics ด้วยสูตรอิสระ ตรวจ threshold ทั้ง 2,028 ค่าและ bootstrap 500 รอบ ผลตรงกัน ความต่างสูงสุด 1.1102230246251565e-16

LightGBM: AP 0.971949038858016; ROC-AUC 0.9930494406351498; Precision 0.7758620689655172; Recall 0.9662576687116564; F1 0.860655737704918; Balanced Accuracy 0.9563641284734752; Brier 0.024354960501739943

TP315 / FP91 / FN11 / TN1609; threshold 0.271024392128117 ตรงกับ frozen policy และ predictions; teaching loss 5×11+91=146 การตัดสิน threshold ไม่ใช้ test ดู [independent_verification.json](independent_verification.json)

## SHAP

อธิบาย Random Forest tuned เท่านั้น ไม่ใช่ LightGBM; positive class index1 ตรง classes[0,1] ตรวจ feature mapping39คอลัมน์ และ additivity error สูงสุด 1.9317880628477724e-14 Local base0.4988689534895673 + SHAP sum0.49870350717451156 = RF probability0.9975724606640949 ทดสอบรูปแบบ API ด้วยข้อมูลจำลอง 8 กรณี รวม class index0 และการปฏิเสธ class ที่ผิด ดู [compatibility_checks.json](compatibility_checks.json)

## ข้อจำกัดที่ยังต้องคงไว้ (INFO)

ไม่มี verified scoring timestamp, feature cutoff, label horizon, treatment, event/censoring time จึงไม่ยืนยัน future forecasting, causality, uplift, survival หรือกำไรจริง SHAP เป็นพฤติกรรมโมเดล ไม่ใช่ treatment effect Retention experiment เป็นข้อเสนออนาคต Features มีความสัมพันธ์กัน; ไม่อ้างว่า SHAP attribution เป็น causal importance หรือ model comparison พิสูจน์ statistical superiority ไม่ปรับโมเดลตาม test เพื่อแก้ข้อจำกัดเหล่านี้

## Repository

เก็บ audit/runtime เดิมเพื่อ provenance ไม่ commit raw Kaggle CSV, OS junk, cache, credentials หรือ private environment paths Archive สร้างใหม่จาก final outputs และ validation report ขนาดทุกไฟล์ต่ำกว่า GitHub limit โดยไม่ใช้ LFS ดู [repository_checks.json](repository_checks.json), [change_log.csv](change_log.csv) และ [workspace_inventory.json](workspace_inventory.json)

รายงานนี้เป็น pre-push audit การยืนยัน commit/remote HEAD ทำหลัง push และรายงานแยกในข้อความส่งมอบ ไม่อ้างว่าการตรวจ local เท่ากับเผยแพร่สำเร็จ
