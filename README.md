# Shaping Recorder (Blender Add-on)

[English](#english) | [中文（简体）](#中文简体) | [中文（繁體）](#中文繁體) | [日本語](#日本語) | [Español](#español) | [Deutsch](#deutsch) | [Français](#français) | [Italiano](#italiano) | [한국어](#한국어) | [Polski](#polski) | [Português](#português) | [Русский](#русский) | [Українська](#українська)

## English

Shaping Recorder records mesh shaping/editing steps (including topology changes) and the active 3D viewport view, then replays them with interpolation. During playback you can optionally export a frame sequence.

**Features**
- Record mesh edits over time and detect undo/redo.
- Record 3D viewport view (location/rotation/zoom).
- Replay with interpolated geometry and view.
- Optional frame-sequence export.

**Installation**
1. Download this repository as a ZIP.
2. In Blender: **Edit → Preferences → Add-ons → Install…**
3. Select the ZIP and enable **Shaping Recorder**.

**Usage**
1. Select a mesh object.
2. Open **View3D → Sidebar → Shaping Recorder**.
3. Click **Start Recording**.
4. Edit the mesh in Edit Mode and move the viewport as desired.
5. Click **Stop Recording**.
6. Click **Play** to replay, or **Record** to export frames.

**Note about viewport recording**
- The recorded view is based on the active 3D Viewport camera transform (the viewport’s own “camera”), not on any scene/user camera object.
- If your model appears too small while recording, adjust the Viewport Camera **Focal Length** in the View panel (N‑panel → View → Focal Length) to scale the overall framing.

**Settings**
- **Step Duration**: seconds per recorded step (mesh phase).
- **Interpolation Steps**: interpolation frames per step.
- **Start Step / End Step**: replay range (End Step 0 = to end).
- **Export Render Mode**:
  - **Viewport**: OpenGL viewport render (fast, may ignore Film Transparent).
  - **Final Render**: scene render engine (respects Film Transparent, lighting, samples).
- **File Prefix**: exported frame filename prefix.

**Compatibility**
- Blender 4.2+

**License**
- GNU General Public License v3.0 or later. See `LICENSE`.

---

## 中文（简体）

Shaping Recorder 用于记录网格形变/编辑步骤（包含拓扑变化）以及当前 3D 视口视角，并通过插值回放整个过程。回放时可选导出帧序列。

**功能**
- 记录网格编辑步骤，并可检测 Undo/Redo。
- 记录 3D 视口视角（位置/旋转/缩放）。
- 插值回放网格与视角变化。
- 可选导出帧序列。

**安装**
1. 下载本仓库 ZIP。
2. Blender：**编辑 → 偏好设置 → 插件 → 安装…**
3. 选择 ZIP 并启用 **Shaping Recorder**。

**使用**
1. 选择一个网格对象。
2. 打开 **3D 视图 → 侧栏 → Shaping Recorder**。
3. 点击 **开始录制**。
4. 在编辑模式下编辑网格，并按需要移动视角。
5. 点击 **停止录制**。
6. 点击 **播放** 仅回放；点击 **录制** 回放并导出帧序列。

**关于视口录制的说明**
- 录制的视角基于当前 3D 视口的“视口摄影机”（Viewport Camera）变换，而不是场景中用户使用的摄影机对象。
- 录制时如果模型看起来太小，可以在右侧 **View** 面板中调整视口摄影机的 **Focal Length（焦距）**（N 面板 → View → Focal Length），以改变整体取景大小。

**设置**
- **步长时间**：每步网格变形阶段的持续秒数。
- **插值步数**：每步之间的插值帧数。
- **起始步 / 结束步**：回放范围（结束步为 0 表示到末尾）。
- **导出渲染模式**：
  - **视口**：使用 OpenGL 视口渲染（速度快，可能不遵循透明背景）。
  - **最终渲染**：使用场景渲染器（遵循透明背景/光照/采样）。
- **文件前缀**：导出帧文件名前缀。

**兼容性**
- Blender 4.2+

**许可证**
- GNU GPL v3.0 或更高版本。详见 `LICENSE`。

---

## 中文（繁體）

Shaping Recorder 用於記錄網格形變/編輯步驟（包含拓撲變化）以及當前 3D 視口視角，並透過插值回放整個過程。回放時可選匯出幀序列。

**功能**
- 記錄網格編輯步驟，並可偵測 Undo/Redo。
- 記錄 3D 視口視角（位置/旋轉/縮放）。
- 插值回放網格與視角變化。
- 可選匯出幀序列。

**安裝**
1. 下載本倉庫 ZIP。
2. Blender：**Edit → Preferences → Add-ons → Install…**
3. 選擇 ZIP 並啟用 **Shaping Recorder**。

**使用**
1. 選擇一個網格物件。
2. 開啟 **View3D → Sidebar → Shaping Recorder**。
3. 點擊 **Start Recording**。
4. 在編輯模式下編輯網格，並按需要移動視角。
5. 點擊 **Stop Recording**。
6. 點擊 **Play** 僅回放；點擊 **Record** 回放並匯出幀序列。

**關於視口錄製的說明**
- 錄製的視角基於當前 3D 視口的 Viewport Camera（視口攝影機）變換，而不是場景中的使用者攝影機物件。
- 錄製時若模型看起來太小，可在右側 **View** 面板調整視口攝影機的 **Focal Length（焦距）**（N 面板 → View → Focal Length），以改變整體取景大小。

**設定**
- **Step Duration**：每步網格變形階段的持續秒數。
- **Interpolation Steps**：每步之間的插值幀數。
- **Start Step / End Step**：回放範圍（End Step 0 = 到末尾）。
- **Export Render Mode**：
  - **Viewport**：OpenGL 視口渲染（速度快，可能忽略透明背景）。
  - **Final Render**：使用場景渲染器（遵循透明背景/光照/採樣）。
- **File Prefix**：匯出幀檔案名前綴。

**相容性**
- Blender 4.2+

**許可證**
- GNU GPL v3.0 或更高版本。詳見 `LICENSE`。


---

## 日本語

Shaping Recorder は、メッシュの形状/編集ステップ（トポロジー変更を含む）と 3D ビューポートの視点を記録し、補間しながら再生します。再生時にフレーム連番を書き出すこともできます。

**機能**
- メッシュ編集ステップの記録と Undo/Redo 検出。
- 3D ビューポート視点（位置/回転/ズーム）の記録。
- メッシュと視点を補間しながら再生。
- フレーム連番の書き出し。

**インストール**
1. このリポジトリを ZIP でダウンロードします。
2. Blender：**Edit → Preferences → Add-ons → Install…**
3. ZIP を選択し **Shaping Recorder** を有効化します。

**使い方**
1. メッシュオブジェクトを選択。
2. **View3D → Sidebar → Shaping Recorder** を開く。
3. **Start Recording** を押す。
4. 編集モードで操作し、必要に応じて視点を移動。
5. **Stop Recording** を押す。
6. **Play** で再生、**Record** で再生しながらフレームを書き出し。

**ビューポート録画について**
- 記録される視点は、3D ビューポートの Viewport Camera（ビューポート側のカメラ）変換に基づきます。シーン内のユーザーカメラには基づきません。
- 録画中にモデルが小さく見える場合は、右側の **View** パネルで Viewport Camera の **Focal Length（焦点距離）**（N パネル → View → Focal Length）を調整して取景サイズを変更できます。

**設定**
- **Step Duration**：各ステップのメッシュ補間時間（秒）。
- **Interpolation Steps**：ステップ間の補間フレーム数。
- **Start Step / End Step**：再生範囲（End Step 0 = 最後まで）。
- **Export Render Mode**：
  - **Viewport**：OpenGL ビューポートレンダー（高速、透明背景を無視する場合あり）。
  - **Final Render**：シーンのレンダーエンジン（透明背景/光/サンプルを反映）。
- **File Prefix**：書き出しフレームの接頭辞。

**対応**
- Blender 4.2+

**ライセンス**
- GPL v3.0 以降。`LICENSE` を参照。

---

## Español

Shaping Recorder registra los pasos de modelado/edición de una malla (incluyendo cambios de topología) y la vista activa del visor 3D, y luego los reproduce con interpolación. Durante la reproducción puedes exportar una secuencia de fotogramas.

**Funciones**
- Registrar ediciones de malla y detectar undo/redo.
- Registrar la vista del visor 3D (posición/rotación/zoom).
- Reproducir con geometría y vista interpoladas.
- Exportación opcional de secuencia de fotogramas.

**Instalación**
1. Descarga este repositorio como ZIP.
2. En Blender: **Edit → Preferences → Add-ons → Install…**
3. Selecciona el ZIP y habilita **Shaping Recorder**.

**Uso**
1. Selecciona un objeto de malla.
2. Abre **View3D → Sidebar → Shaping Recorder**.
3. Pulsa **Start Recording**.
4. Edita la malla en modo Edición y mueve la vista según necesites.
5. Pulsa **Stop Recording**.
6. Pulsa **Play** para reproducir, o **Record** para exportar fotogramas.

**Nota sobre la grabación del visor**
- La vista grabada se basa en la transformación de la cámara del Viewport 3D activo (la “cámara del visor”), no en ninguna cámara de escena/usuario.
- Si el modelo se ve demasiado pequeño al grabar, ajusta la **Focal Length (distancia focal)** de la cámara del visor en el panel **View** (N‑panel → View → Focal Length) para cambiar el encuadre general.

**Ajustes**
- **Step Duration**: segundos por paso (fase de malla).
- **Interpolation Steps**: fotogramas de interpolación por paso.
- **Start Step / End Step**: rango de reproducción (End Step 0 = hasta el final).
- **Export Render Mode**:
  - **Viewport**: render OpenGL del visor (rápido, puede ignorar fondo transparente).
  - **Final Render**: motor de render de la escena (respeta fondo transparente, luz, muestras).
- **File Prefix**: prefijo de los archivos exportados.

**Compatibilidad**
- Blender 4.2+

**Licencia**
- GNU GPL v3.0 o posterior. Ver `LICENSE`.

---

## Deutsch

Shaping Recorder zeichnet Mesh‑Formungs-/Bearbeitungsschritte (einschließlich Topologieänderungen) sowie die aktive 3D‑Viewport‑Ansicht auf und spielt sie anschließend mit Interpolation ab. Während der Wiedergabe kannst du optional eine Frame‑Sequenz exportieren.

**Funktionen**
- Mesh‑Bearbeitungsschritte aufzeichnen und Undo/Redo erkennen.
- 3D‑Viewport‑Ansicht (Position/Rotation/Zoom) aufzeichnen.
- Mit interpolierter Geometrie und Ansicht wiedergeben.
- Optionaler Export einer Frame‑Sequenz.

**Installation**
1. Dieses Repository als ZIP herunterladen.
2. In Blender: **Edit → Preferences → Add-ons → Install…**
3. ZIP auswählen und **Shaping Recorder** aktivieren.

**Verwendung**
1. Ein Mesh‑Objekt auswählen.
2. **View3D → Sidebar → Shaping Recorder** öffnen.
3. **Start Recording** klicken.
4. Im Edit‑Modus das Mesh bearbeiten und die Ansicht bewegen.
5. **Stop Recording** klicken.
6. **Play** zum Abspielen oder **Record** zum Exportieren.

**Hinweis zur Viewport‑Aufnahme**
- Die aufgezeichnete Ansicht basiert auf der aktiven 3D‑Viewport‑Kameratransformation (der Viewport‑eigenen „Kamera“), nicht auf einer Szenen-/Benutzerkamera.
- Wenn das Modell beim Aufnehmen zu klein wirkt, stelle die **Focal Length (Brennweite)** der Viewport‑Kamera im **View**‑Panel ein (N‑Panel → View → Focal Length), um den Bildausschnitt zu skalieren.

**Einstellungen**
- **Step Duration**: Sekunden pro Schritt (Mesh‑Phase).
- **Interpolation Steps**: Interpolationsframes pro Schritt.
- **Start Step / End Step**: Wiedergabebereich (End Step 0 = bis zum Ende).
- **Export Render Mode**:
  - **Viewport**: OpenGL‑Viewport‑Render (schnell, kann Film Transparent ignorieren).
  - **Final Render**: Szenen‑Render‑Engine (respektiert Film Transparent, Licht, Samples).
- **File Prefix**: Dateipräfix für exportierte Frames.

**Kompatibilität**
- Blender 4.2+

**Lizenz**
- GNU GPL v3.0 oder höher. Siehe `LICENSE`.

---

## Français

Shaping Recorder enregistre les étapes de façonnage/édition d’un maillage (y compris les changements de topologie) ainsi que la vue active du Viewport 3D, puis les rejoue avec interpolation. Pendant la lecture, tu peux exporter une séquence d’images.

**Fonctionnalités**
- Enregistrer les étapes d’édition et détecter undo/redo.
- Enregistrer la vue du Viewport 3D (position/rotation/zoom).
- Rejouer avec géométrie et vue interpolées.
- Export optionnel d’une séquence d’images.

**Installation**
1. Télécharger ce dépôt en ZIP.
2. Dans Blender : **Edit → Preferences → Add-ons → Install…**
3. Sélectionner le ZIP et activer **Shaping Recorder**.

**Utilisation**
1. Sélectionner un objet maillage.
2. Ouvrir **View3D → Sidebar → Shaping Recorder**.
3. Cliquer sur **Start Recording**.
4. Éditer le maillage en mode Édition et déplacer la vue.
5. Cliquer sur **Stop Recording**.
6. Cliquer sur **Play** pour rejouer ou **Record** pour exporter.

**Remarque sur l’enregistrement du viewport**
- La vue enregistrée est basée sur la transformation de la caméra du Viewport 3D actif (la « caméra du viewport »), et non sur une caméra de scène/utilisateur.
- Si le modèle paraît trop petit pendant l’enregistrement, ajuste la **Focal Length (longueur focale)** de la caméra du viewport dans le panneau **View** (N‑panel → View → Focal Length) pour modifier le cadrage global.

**Paramètres**
- **Step Duration** : secondes par étape (phase maillage).
- **Interpolation Steps** : images interpolées par étape.
- **Start Step / End Step** : plage de lecture (End Step 0 = jusqu’à la fin).
- **Export Render Mode** :
  - **Viewport** : rendu OpenGL du viewport (rapide, peut ignorer Film Transparent).
  - **Final Render** : moteur de rendu de la scène (respecte Film Transparent, éclairage, échantillons).
- **File Prefix** : préfixe des fichiers exportés.

**Compatibilité**
- Blender 4.2+

**Licence**
- GNU GPL v3.0 ou ultérieure. Voir `LICENSE`.

---

## Italiano

Shaping Recorder registra i passaggi di modellazione/modifica della mesh (inclusi i cambi di topologia) e la vista attiva del Viewport 3D, quindi li riproduce con interpolazione. Durante la riproduzione puoi esportare una sequenza di fotogrammi.

**Funzionalità**
- Registrare i passaggi di modifica e rilevare undo/redo.
- Registrare la vista del Viewport 3D (posizione/rotazione/zoom).
- Riprodurre con geometria e vista interpolate.
- Esportazione opzionale di una sequenza di fotogrammi.

**Installazione**
1. Scarica questo repository come ZIP.
2. In Blender: **Edit → Preferences → Add-ons → Install…**
3. Seleziona lo ZIP e abilita **Shaping Recorder**.

**Uso**
1. Seleziona un oggetto mesh.
2. Apri **View3D → Sidebar → Shaping Recorder**.
3. Clicca **Start Recording**.
4. Modifica la mesh in modalità Edit e muovi la vista.
5. Clicca **Stop Recording**.
6. Clicca **Play** per riprodurre o **Record** per esportare.

**Nota sulla registrazione del viewport**
- La vista registrata si basa sulla trasformazione della camera del Viewport 3D attivo (la “camera del viewport”), non su una camera di scena/utente.
- Se il modello appare troppo piccolo durante la registrazione, regola la **Focal Length (lunghezza focale)** della camera del viewport nel pannello **View** (N‑panel → View → Focal Length) per cambiare l’inquadratura complessiva.

**Impostazioni**
- **Step Duration**: secondi per passo (fase mesh).
- **Interpolation Steps**: fotogrammi di interpolazione per passo.
- **Start Step / End Step**: intervallo di riproduzione (End Step 0 = fino alla fine).
- **Export Render Mode**:
  - **Viewport**: render OpenGL del viewport (rapido, può ignorare Film Transparent).
  - **Final Render**: motore di render della scena (rispetta Film Transparent, luci, campioni).
- **File Prefix**: prefisso dei file esportati.

**Compatibilità**
- Blender 4.2+

**Licenza**
- GNU GPL v3.0 o successiva. Vedi `LICENSE`.

---

## 한국어

Shaping Recorder는 메시 형상/편집 단계(토폴로지 변경 포함)와 활성 3D 뷰포트 시점을 기록한 뒤, 보간으로 재생합니다. 재생 중 프레임 시퀀스를 내보낼 수 있습니다.

**기능**
- 메시 편집 단계를 기록하고 Undo/Redo를 감지.
- 3D 뷰포트 시점(위치/회전/줌) 기록.
- 보간된 지오메트리와 시점으로 재생.
- 선택적 프레임 시퀀스 내보내기.

**설치**
1. 이 저장소를 ZIP으로 다운로드.
2. Blender에서 **Edit → Preferences → Add-ons → Install…**
3. ZIP을 선택하고 **Shaping Recorder**를 활성화.

**사용법**
1. 메시 오브젝트를 선택.
2. **View3D → Sidebar → Shaping Recorder**를 엽니다.
3. **Start Recording**을 클릭.
4. 편집 모드에서 메시를 편집하고 시점을 이동.
5. **Stop Recording**을 클릭.
6. **Play**로 재생하거나 **Record**로 내보내기.

**뷰포트 기록 안내**
- 기록되는 시점은 활성 3D 뷰포트의 Viewport Camera(뷰포트 자체 카메라) 변환을 기준으로 하며, 장면/사용자 카메라 오브젝트를 기준으로 하지 않습니다.
- 기록 중 모델이 너무 작게 보이면 **View** 패널에서 Viewport Camera의 **Focal Length(초점 거리)**를 조정하세요 (N 패널 → View → Focal Length). 전체 프레이밍 크기가 바뀝니다.

**설정**
- **Step Duration**: 단계당 시간(초).
- **Interpolation Steps**: 단계당 보간 프레임 수.
- **Start Step / End Step**: 재생 범위(End Step 0 = 끝까지).
- **Export Render Mode**:
  - **Viewport**: OpenGL 뷰포트 렌더(빠름, Film Transparent 무시 가능).
  - **Final Render**: 장면 렌더 엔진(Film Transparent/조명/샘플 반영).
- **File Prefix**: 내보낸 프레임 파일 접두사.

**호환성**
- Blender 4.2+

**라이선스**
- GNU GPL v3.0 이상. `LICENSE` 참고.

---

## Polski

Shaping Recorder zapisuje kroki kształtowania/edycji siatki (w tym zmiany topologii) oraz aktywny widok 3D, a następnie odtwarza je z interpolacją. Podczas odtwarzania możesz eksportować sekwencję klatek.

**Funkcje**
- Rejestrowanie kroków edycji i wykrywanie undo/redo.
- Rejestrowanie widoku 3D (pozycja/obrót/zoom).
- Odtwarzanie z interpolowaną geometrią i widokiem.
- Opcjonalny eksport sekwencji klatek.

**Instalacja**
1. Pobierz to repozytorium jako ZIP.
2. W Blenderze: **Edit → Preferences → Add-ons → Install…**
3. Wybierz ZIP i włącz **Shaping Recorder**.

**Użycie**
1. Wybierz obiekt siatki.
2. Otwórz **View3D → Sidebar → Shaping Recorder**.
3. Kliknij **Start Recording**.
4. Edytuj siatkę w trybie Edycji i poruszaj widokiem.
5. Kliknij **Stop Recording**.
6. Kliknij **Play** aby odtworzyć lub **Record** aby wyeksportować.

**Uwaga o nagrywaniu widoku**
- Zapisany widok opiera się na transformacji kamery aktywnego Viewportu 3D (kamerze viewportu), a nie na kamerze sceny/użytkownika.
- Jeśli model wygląda zbyt mało podczas nagrywania, zmień **Focal Length (ogniskową)** kamery viewportu w panelu **View** (N‑panel → View → Focal Length), aby przeskalować ujęcie.

**Ustawienia**
- **Step Duration**: sekundy na krok.
- **Interpolation Steps**: klatki interpolacji na krok.
- **Start Step / End Step**: zakres odtwarzania (End Step 0 = do końca).
- **Export Render Mode**:
  - **Viewport**: render OpenGL widoku (szybki, może ignorować Film Transparent).
  - **Final Render**: silnik renderu sceny (respektuje Film Transparent, światło, próbki).
- **File Prefix**: prefiks nazw eksportowanych klatek.

**Kompatybilność**
- Blender 4.2+

**Licencja**
- GNU GPL v3.0 lub nowsza. Zobacz `LICENSE`.

---

## Português

Shaping Recorder grava passos de modelagem/edição de malha (incluindo mudanças de topologia) e a vista ativa do Viewport 3D, e depois reproduz com interpolação. Durante a reprodução você pode exportar uma sequência de quadros.

**Recursos**
- Gravar passos de edição e detectar undo/redo.
- Gravar a vista do Viewport 3D (posição/rotação/zoom).
- Reproduzir com geometria e vista interpoladas.
- Exportação opcional de sequência de quadros.

**Instalação**
1. Baixe este repositório como ZIP.
2. No Blender: **Edit → Preferences → Add-ons → Install…**
3. Selecione o ZIP e habilite **Shaping Recorder**.

**Uso**
1. Selecione um objeto de malha.
2. Abra **View3D → Sidebar → Shaping Recorder**.
3. Clique em **Start Recording**.
4. Edite a malha no modo Edit e mova a vista.
5. Clique em **Stop Recording**.
6. Clique em **Play** para reproduzir ou **Record** para exportar.

**Nota sobre a gravação do viewport**
- A vista gravada é baseada na transformação da câmera do Viewport 3D ativo (a “câmera do viewport”), e não em uma câmera de cena/usuário.
- Se o modelo parecer muito pequeno durante a gravação, ajuste a **Focal Length (distância focal)** da câmera do viewport no painel **View** (N‑panel → View → Focal Length) para alterar o enquadramento geral.

**Configurações**
- **Step Duration**: segundos por passo.
- **Interpolation Steps**: quadros de interpolação por passo.
- **Start Step / End Step**: faixa de reprodução (End Step 0 = até o fim).
- **Export Render Mode**:
  - **Viewport**: render OpenGL do viewport (rápido, pode ignorar Film Transparent).
  - **Final Render**: motor de render da cena (respeita Film Transparent, luz, amostras).
- **File Prefix**: prefixo dos arquivos exportados.

**Compatibilidade**
- Blender 4.2+

**Licença**
- GNU GPL v3.0 ou posterior. Ver `LICENSE`.

---

## Русский

Shaping Recorder записывает шаги формирования/редактирования меша (включая изменения топологии) и активный вид 3D‑вьюпорта, а затем воспроизводит их с интерполяцией. Во время воспроизведения можно экспортировать последовательность кадров.

**Возможности**
- Запись шагов редактирования меша и обнаружение undo/redo.
- Запись вида 3D‑вьюпорта (позиция/поворот/зум).
- Воспроизведение с интерполированной геометрией и видом.
- Опциональный экспорт последовательности кадров.

**Установка**
1. Скачайте репозиторий как ZIP.
2. В Blender: **Edit → Preferences → Add-ons → Install…**
3. Выберите ZIP и включите **Shaping Recorder**.

**Использование**
1. Выберите меш‑объект.
2. Откройте **View3D → Sidebar → Shaping Recorder**.
3. Нажмите **Start Recording**.
4. Редактируйте меш в режиме Edit и перемещайте вид.
5. Нажмите **Stop Recording**.
6. Нажмите **Play** для воспроизведения или **Record** для экспорта.

**Примечание о записи вида**
- Записываемый вид основан на трансформации камеры активного 3D‑вьюпорта (камеры вьюпорта), а не на камере сцены/пользователя.
- Если модель выглядит слишком маленькой при записи, измените **Focal Length (фокусное расстояние)** камеры вьюпорта в панели **View** (N‑panel → View → Focal Length), чтобы подстроить общий масштаб кадра.

**Настройки**
- **Step Duration**: секунд на шаг.
- **Interpolation Steps**: интерполяционных кадров на шаг.
- **Start Step / End Step**: диапазон воспроизведения (End Step 0 = до конца).
- **Export Render Mode**:
  - **Viewport**: OpenGL‑рендер вьюпорта (быстро, может игнорировать Film Transparent).
  - **Final Render**: движок рендера сцены (учитывает Film Transparent, свет, сэмплы).
- **File Prefix**: префикс имен экспортируемых кадров.

**Совместимость**
- Blender 4.2+

**Лицензия**
- GNU GPL v3.0 или новее. См. `LICENSE`.

---

## Українська

Shaping Recorder записує кроки формування/редагування меша (включно зі змінами топології) та активний вид 3D‑в'юпорта, а потім відтворює їх з інтерполяцією. Під час відтворення можна експортувати послідовність кадрів.

**Можливості**
- Запис кроків редагування меша та виявлення undo/redo.
- Запис виду 3D‑в'юпорта (позиція/обертання/зум).
- Відтворення з інтерпольованою геометрією та видом.
- Опційний експорт послідовності кадрів.

**Встановлення**
1. Завантажте це репозиторій як ZIP.
2. У Blender: **Edit → Preferences → Add-ons → Install…**
3. Виберіть ZIP і увімкніть **Shaping Recorder**.

**Використання**
1. Виберіть об'єкт‑меш.
2. Відкрийте **View3D → Sidebar → Shaping Recorder**.
3. Натисніть **Start Recording**.
4. Редагуйте меш у режимі Edit і рухайте вид.
5. Натисніть **Stop Recording**.
6. Натисніть **Play** для відтворення або **Record** для експорту.

**Примітка про запис виду**
- Записаний вид базується на трансформації камери активного 3D‑в'юпорта (камери в'юпорта), а не на камері сцени/користувача.
- Якщо модель виглядає занадто маленькою під час запису, змініть **Focal Length (фокусну відстань)** камери в'юпорта у панелі **View** (N‑panel → View → Focal Length), щоб підлаштувати загальний масштаб кадру.

**Налаштування**
- **Step Duration**: секунд на крок.
- **Interpolation Steps**: інтерполяційних кадрів на крок.
- **Start Step / End Step**: діапазон відтворення (End Step 0 = до кінця).
- **Export Render Mode**:
  - **Viewport**: OpenGL‑рендер в'юпорта (швидко, може ігнорувати Film Transparent).
  - **Final Render**: рушій рендера сцени (враховує Film Transparent, світло, семпли).
- **File Prefix**: префікс імен експортованих кадрів.

**Сумісність**
- Blender 4.2+

**Ліцензія**
- GNU GPL v3.0 або новіша. Див. `LICENSE`.
