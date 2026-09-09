# OnozIdle — Unity Headless Test Durumu ve Analiz Raporu

**Tarih:** 2026-09-09  
**Kapsam:** `onoz-idle` (`C:\Users\pc\Unity Projeleri\OnozIdle`)

---

## 1. Makine ve Unity Editor Durumu

- **Unity Editor Yolu:** `C:\Program Files\Unity\Hub\Editor\6000.3.20f1\Editor\Unity.exe`
- **Sürüm:** `6000.3.20f1 (c9ba695d4f07)` — `ProjectSettings/ProjectVersion.txt` ile birebir uyumlu.
- **Lisans:** Unity Personal (Assigned, Expiration: Unlimited) — lisans doğrulandı ve aktif.

---

## 2. Headless Test Runner (`-runTests`) Doğrulama Sonuçları

`Unity.exe -batchmode -nographics -projectPath ... -runTests -testPlatform EditMode` komutu bizzat çalıştırılarak test edilmiştir. Alınan somut bulgular:

1. **Test Paketi Yokluğu:**  
   Projede (`Assets/`) hiçbir birim test scripti veya test assembly'si (`.asmdef`) tanımlı değildir.  
   Unity log çıktısı:  
   `Test run completed. Exiting with code 0 (Ok). No tests were executed.`  
   Yani var olmayan bir test paketi üzerinden "geçti" almak sahte bir taban çizgisi oluşturur (KA-07 tuzağı).

2. **Git Çalışma Ağacının Kirlenmesi (Kırmızı Çizgi 5 İhlali):**  
   `-runTests` çalıştırıldığında:
   - Proje köküne `editmode_results.xml` dosyası oluşturulmaktadır (untracked).
   - `ProjectSettings/ProjectSettings.asset` dosyası Unity tarafından sessizce değiştirilmekte (`scriptingDefineSymbols.Android` içinden `SENTIS_ANALYTICS_ENABLED` silinmektedir).
   - Bu durum her eval koşusundan sonra projenin git çalışma ağacını kirletmektedir (`git status --porcelain` temiz kalmamaktadır).

3. **Çalışma Süresi ve Yan Süreçler:**  
   - Tek bir headless koşum yaklaşık **48 saniye** sürmektedir.
   - Arka planda `unity-ai-relay` (port 9001/9002) ve ADB süreçleri tetiklenmektedir.

4. **Eşzamanlılık Kilitlenmesi:**  
   Geliştirici Unity Editor arayüzünü açık tuttuğunda, `Temp/UnityLockfile` sebebiyle batchmode süreci hata vermekte ve çalışamamaktadır.

---

## 3. Alınan Karar ve Regresyon Seti Tasarımı

**"Boş set, yalancı setten iyidir."** ilkesi gereğince, hiçbir test içermeyen ve çalışma ağacını kirleten `-runTests` komutu bir eval görevi olarak **eklenmemiştir**.

Bunun yerine, Unity Editor gerektirmeyen, milisaniyeler içinde koşan, deterministik ve çalışma ağacını %100 temiz bırakan şu regresyon kontrolleri `tasks.jsonl` içine alınmıştır:

1. **`IDLE-01` (Asset/.meta Çift Bütünlüğü):**  
   Unity projelerinde en kritik veri kaybı riski, bir asset dosyasının `.meta` dosyasını kaybetmesi veya sahipsiz `.meta` kalmasıdır. Tüm `Assets/` ağacı taranarak eksik veya artık `.meta` dosyaları doğrulanır.
2. **`IDLE-02` (ProjectSettings ve Sahne Referans Bütünlüğü):**  
   `ProjectVersion.txt` içindeki editör sürüm bildirimi ve `EditorBuildSettings.asset` içinde tanımlanmış build sahnelerinin diskte fiziksel olarak var olduğu teyit edilir.

İleride projeye gerçek bir `Tests/` paketi ve `.asmdef` eklendiğinde, ağaç kirliliğini temizleyen bir teardown mekanizmasıyla birlikte test koşumu görevi sete dahil edilebilir.
