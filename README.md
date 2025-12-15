# Shaping Recorder (Blender Add-on)

[English](#english) | [中文 (简体)](#中文简体) | [中文 (繁體)](#中文繁體) | [日本語](#日本語) | [Español](#español) | [Deutsch](#deutsch) | [Français](#français) | [Italiano](#italiano) | [한국어](#한국어) | [Polski](#polski) | [Português (Brasil)](#português-brasil) | [Português (Portugal)](#português-portugal) | [Русский](#русский) | [Українська](#українська)

---

## English

**Shaping Recorder** is a helper add-on designed for creating Blender modeling and sculpting tutorials. It records every mesh deformation, topology change, and corresponding camera angle, allowing for smooth playback and rendering of these processes.

### Core Features
*   **Full Process Recording**: Supports topology changes in Edit Mode (Extrude, Bevel, Loop Cuts, etc.) and deformations in Sculpt Mode (supports Remesh, but **does NOT support Dyntopo/Dynamic Topology**).
*   **Multi-Object Support**: Record multiple different objects in the scene independently. Switching the selected object switches the recording data. Data is saved with the `.blend` file.
*   **Smart Playback**: Automatically generates smooth interpolated animation between steps.
*   **Post-Adjustment**: After recording, you can freely modify the camera angle and duration for each step, or even delete unwanted steps without re-recording.

### Installation
1.  Download the add-on ZIP file.
2.  Open Blender and go to **Edit → Preferences → Add-ons**.
3.  Click **Install**, select the ZIP file, and enable **Shaping Recorder**.
4.  Find the add-on panel in the 3D Viewport Sidebar (N-key).

### Basic Usage
1.  Select a mesh object.
2.  Click **"Start Recording"** in the add-on panel.
3.  Perform modeling or sculpting operations (each completed operation is treated as a "step").
4.  Adjust the viewport angle at any time during the process; the add-on records the view at each step.
5.  Click **"Stop Recording"** when finished.
6.  Click **"Play"** to preview the result.

### Advanced Editing & Settings
After recording, you can fine-tune each step via the list:

#### 1. Step Management
*   **List Navigation**: Clicking on a step in the list jumps the viewport to that step's state and angle.
*   **Delete/Re-record**: If a step is unsatisfactory, delete it, or continue adding subsequent operations from that step via "Record".

#### 2. Camera Adjustment
*   **Reset Perspective**: If a view is poor (e.g., obstructed) at a certain step, select it in the list, adjust the viewport, and click **"Reset Camera Position"**. The playback will smoothly transition to this new angle.

#### 3. Visual Marking (Edge Highlight)
*   **Mark Edges**: To clearly show which edges were operated on, enable "Edge Display" for a step, click "Mark Edge", enter Edit Mode, and select specific edges.
*   **Style Adjustment**: Supports custom color and width for highlighted edges.
*   **Geometry Nodes Support**: Marked edges generate an attribute named `New Edge`. You can use this with Geometry Nodes to create cool custom effects (e.g., glowing lines, outlines).

#### 4. Time Control (Key Feature)
The add-on separates animation into "Camera Movement" and "Mesh Deformation", allowing independent duration control:
*   **Global Settings**:
    *   **Camera Duration**: Time taken to move the camera from the previous step to the current one.
    *   **Mesh Duration**: Time taken for the model to morph from the previous shape to the current one.
    *   *Tip: Increasing time makes actions smoother; decreasing makes them snappier.*
*   **Custom Timing (Per Step)**: Check **"Custom Timing"** for a step to set Camera and Mesh durations specific to that step (e.g., slow motion for key steps, fast forward for transitions).

#### 5. Playback & Render Range
*   **Playback Mode**:
    *   **From Start**: Play from step 0 to the end.
    *   **From Active**: Start playing from the currently selected step.
*   **Range Settings**: Use **"Set Start"** and **"Set End"** buttons to specify a specific interval for playback/rendering (e.g., render only steps 3 to 7).

### Export & Render
The "Output" panel offers two export modes:
*   **Viewport**: Similar to "Viewport Render Animation", fast and WYSIWYG.
*   **Render**: Uses the current render engine (Eevee/Cycles) for final output, supporting lighting and materials.
*   **Format Control**: The output format (image sequence or video) depends on Blender's "Output Properties" panel settings.

### Notes
*   **Dyntopo**: Do NOT use Dyntopo (Dynamic Topology) in Sculpt Mode, as it causes unpredictable vertex changes that break interpolation. Use Remesh instead.
*   **Data Saving**: All recorded data (steps, angles, marks) is saved within the current `.blend` file.

**Compatibility**
- Blender 4.2+

**License**
- GNU GPL v3.0 or later. See `LICENSE`.

---

## 中文（简体）

**Shaping Recorder** 是一款专为制作 Blender 建模/雕刻教程视频设计的辅助插件。它可以记录对象的每一步网格形变、拓扑结构变化以及对应的摄像机视角，并能平滑地回放和渲染这些过程。

### 核心功能
*   **全过程记录**：支持记录编辑模式（Edit Mode）下的挤出、倒角、加线等拓扑变化，以及雕刻模式（Sculpt Mode）下的形变（支持 Remesh 重构网格，**不支持 Dyntopo 动态拓扑**）。
*   **多对象支持**：可以在场景中对多个不同的物体分别进行记录，切换选中物体即可切换记录数据，数据随 `.blend` 文件保存。
*   **智能回放**：自动在步骤之间生成平滑的插值动画。
*   **后期调整**：录制完成后，可以随意修改每一步的摄像机角度、时长，甚至删除不需要的步骤，无需重新录制。

### 安装方法
1.  下载插件 ZIP 文件。
2.  在 Blender 中打开 **编辑 (Edit) → 偏好设置 (Preferences) → 插件 (Add-ons)**。
3.  点击 **安装 (Install)**，选择 ZIP 文件并启用 **Shaping Recorder**。
4.  在 3D 视图的侧栏（N键）中找到插件面板。

### 基本使用流程
1.  选中一个网格对象。
2.  在插件面板中点击 **“开始录制”**。
3.  进行建模或雕刻操作（每完成一个操作视为一个“步骤”）。
4.  在操作过程中，可以随时调整视口角度，插件会记录每一步时的视角。
5.  操作完成后，点击 **“停止录制”**。
6.  点击 **“播放”** 预览效果。

### 高级编辑与设置
录制完成后，你可以通过列表对每一步进行精细调整：

#### 1. 步骤管理
*   **列表导航**：点击列表中的某一步，视口会跳转到该步骤的状态和视角。
*   **删除/重录**：如果某一步操作不满意，可以删除该步骤，或从该步骤通过“录制”继续添加后续操作。

#### 2. 摄像机调整
*   **重设视角**：如果在某一步觉得视角不好（例如被遮挡），可以在列表中选中该步骤，调整好视口角度，然后点击 **“重设摄像机位置”**。回放时，摄像机将平滑过渡到这个新角度。

#### 3. 视觉标记（高亮边）
*   **标记边 (Mark Edges)**：为了在教程中清晰展示当前操作了哪些边，可以在某一步骤开启“边显示”，点击“标记边”进入编辑模式选中特定的边。
*   **样式调整**：支持自定义高亮边的颜色和粗细。
*   **几何节点支持**：标记的边会生成一个名为 `New Edge` 的属性，你可以配合几何节点（Geometry Nodes）制作更酷炫的自定义特效（如流光、描边等）。

#### 4. 时间控制（关键特性）
插件将动画分为“摄像机运动”和“网格形变”两个部分，可分别控制时长：
*   **全局设置**：
    *   **相机持续时间**：摄像机从上一步位置移动到当前位置所需的时间。
    *   **网格持续时间**：模型从上一步形态变化到当前形态所需的时间。
    *   *技巧：增加时间可以让动作更平滑，减少时间则更干脆。*
*   **自定义时间 (每步独立)**：勾选某一步骤的 **“自定义时间”**，可以单独为该步骤设置不同于全局的相机和网格时长（例如，重点步骤慢放，过渡步骤快进）。

#### 5. 播放与渲染范围
*   **播放模式**：
    *   **从头开始**：从第 0 步播放到结束。
    *   **来自活动项**：从当前选中的步骤开始播放。
*   **范围设置**：通过 **“设置开始”** 和 **“设置结束”** 按钮，可以指定只播放/渲染特定的步骤区间（例如只渲染第 3 步到第 7 步）。

### 导出与渲染
在“输出”面板中，提供两种导出模式：
*   **视图 (Viewport)**：类似于“视图渲染动画”，速度快，所见即所得。
*   **渲染 (Render)**：使用当前的渲染引擎（Eevee/Cycles）进行最终渲染，支持光影和材质。
*   **格式控制**：输出格式（图片序列或视频）取决于 Blender “输出属性”面板中的文件格式设置。如果是图片格式则输出序列帧，如果是视频格式则直接输出视频文件。

### 注意事项
*   **Dyntopo**：雕刻模式下请勿使用 Dyntopo（动态拓扑），因为它会产生无法预测的顶点变化，导致插值失败。请使用 Remesh（重构网格）代替。
*   **数据保存**：所有录制的数据（步骤、视角、标记）均保存在当前的 `.blend` 文件中，下次打开可继续编辑。

**兼容性**
- Blender 4.2+

**许可证**
- GNU GPL v3.0 或更高版本。详见 `LICENSE`。

---

## 中文（繁體）

**Shaping Recorder** 是一款專為製作 Blender 建模/雕刻教學影片設計的輔助插件。它可以記錄物件的每一步網格形變、拓撲結構變化以及對應的攝影機視角，並能平滑地回放和渲染這些過程。

### 核心功能
*   **全過程記錄**：支援記錄編輯模式（Edit Mode）下的擠出、倒角、加線等拓撲變化，以及雕刻模式（Sculpt Mode）下的形變（支援 Remesh 重構網格，**不支援 Dyntopo 動態拓撲**）。
*   **多物件支援**：可以在場景中對多個不同的物體分別進行記錄，切換選取物體即可切換記錄數據，數據隨 `.blend` 檔案保存。
*   **智能回放**：自動在步驟之間生成平滑的插值動畫。
*   **後期調整**：錄製完成後，可以隨意修改每一步的攝影機角度、時長，甚至刪除不需要的步驟，無需重新錄製。

### 安裝方法
1.  下載插件 ZIP 檔案。
2.  在 Blender 中開啟 **編輯 (Edit) → 偏好設定 (Preferences) → 插件 (Add-ons)**。
3.  點擊 **安裝 (Install)**，選擇 ZIP 檔案並啟用 **Shaping Recorder**。
4.  在 3D 視圖的側欄（N鍵）中找到插件面板。

### 基本使用流程
1.  選取一個網格物件。
2.  在插件面板中點擊 **「開始錄製」**。
3.  進行建模或雕刻操作（每完成一個操作視為一個「步驟」）。
4.  在操作過程中，可以隨時調整視口角度，插件會記錄每一步時的視角。
5.  操作完成後，點擊 **「停止錄製」**。
6.  點擊 **「播放」** 預覽效果。

### 進階編輯與設定
錄製完成後，你可以透過列表對每一步進行精細調整：

#### 1. 步驟管理
*   **列表導航**：點擊列表中的某一步，視口會跳轉到該步驟的狀態和視角。
*   **刪除/重錄**：如果某一步操作不滿意，可以刪除該步驟，或從該步驟透過「錄製」繼續添加後續操作。

#### 2. 攝影機調整
*   **重設視角**：如果在某一步覺得視角不好（例如被遮擋），可以在列表中選取該步驟，調整好視口角度，然後點擊 **「重設攝影機位置」**。回放時，攝影機將平滑過渡到這個新角度。

#### 3. 視覺標記（高亮邊）
*   **標記邊 (Mark Edges)**：為了在教學中清晰展示當前操作了哪些邊，可以在某一步驟開啟「邊顯示」，點擊「標記邊」進入編輯模式選取特定的邊。
*   **樣式調整**：支援自訂高亮邊的顏色和粗細。
*   **幾何節點支援**：標記的邊會生成一個名為 `New Edge` 的屬性，你可以配合幾何節點（Geometry Nodes）製作更酷炫的自訂特效（如流光、描邊等）。

#### 4. 時間控制（關鍵特性）
插件將動畫分為「攝影機運動」和「網格形變」兩個部分，可分別控制時長：
*   **全局設定**：
    *   **相機持續時間**：攝影機從上一步位置移動到當前位置所需的時間。
    *   **網格持續時間**：模型從上一步形態變化到當前形態所需的時間。
    *   *技巧：增加時間可以讓動作更平滑，減少時間則更乾脆。*
*   **自訂時間 (每步獨立)**：勾選某一步驟的 **「自訂時間」**，可以單獨為該步驟設定不同於全局的相機和網格時長（例如，重點步驟慢放，過渡步驟快進）。

#### 5. 播放與渲染範圍
*   **播放模式**：
    *   **從頭開始**：從第 0 步播放到結束。
    *   **來自活動項**：從當前選取的步驟開始播放。
*   **範圍設定**：透過 **「設定開始」** 和 **「設定結束」** 按鈕，可以指定只播放/渲染特定的步驟區間（例如只渲染第 3 步到第 7 步）。

### 匯出與渲染
在「輸出」面板中，提供兩種匯出模式：
*   **視圖 (Viewport)**：類似於「視圖渲染動畫」，速度快，所見即所得。
*   **渲染 (Render)**：使用當前的渲染引擎（Eevee/Cycles）進行最終渲染，支援光影和材質。
*   **格式控制**：輸出格式（圖片序列或影片）取決於 Blender 「輸出屬性」面板中的檔案格式設定。如果是圖片格式則輸出序列幀，如果是影片格式則直接輸出影片檔案。

### 注意事項
*   **Dyntopo**：雕刻模式下請勿使用 Dyntopo（動態拓撲），因為它會產生無法預測的頂點變化，導致插值失敗。請使用 Remesh（重構網格）代替。
*   **數據保存**：所有錄製的數據（步驟、視角、標記）均保存在當前的 `.blend` 檔案中，下次開啟可繼續編輯。

---

## 日本語

**Shaping Recorder** は、Blenderのモデリングやスカルプトのチュートリアル動画作成のために設計された補助アドオンです。オブジェクトの各メッシュ変形、トポロジー構造の変更、および対応するカメラアングルを記録し、それらのプロセスを滑らかに再生・レンダリングできます。

### 主な機能
*   **全プロセス記録**: 編集モード（Edit Mode）での押し出し、ベベル、ループカットなどのトポロジー変更、およびスカルプトモード（Sculpt Mode）での変形を記録（リメッシュはサポートしますが、**Dyntopo/ダイナミックトポロジーは非対応**）。
*   **マルチオブジェクト対応**: シーン内の複数の異なるオブジェクトを個別に記録できます。選択オブジェクトを切り替えるだけで記録データも切り替わり、データは `.blend` ファイルと共に保存されます。
*   **スマート再生**: ステップ間に滑らかな補間アニメーションを自動生成します。
*   **ポスト編集**: 録画完了後、再録画することなく、各ステップのカメラアングルや期間を自由に変更したり、不要なステップを削除したりできます。

### インストール方法
1.  アドオンの ZIP ファイルをダウンロードします。
2.  Blenderで **編集 (Edit) → プリファレンス (Preferences) → アドオン (Add-ons)** を開きます。
3.  **インストール (Install)** をクリックし、ZIP ファイルを選択して **Shaping Recorder** を有効にします。
4.  3Dビューポートのサイドバー（Nキー）にアドオンパネルが表示されます。

### 基本的な使い方
1.  メッシュオブジェクトを選択します。
2.  アドオンパネルで **「記録開始 (Start Recording)」** をクリックします。
3.  モデリングまたはスカルプト操作を行います（1つの操作が完了するごとに「ステップ」として扱われます）。
4.  操作中、いつでもビューポートの角度を調整できます。アドオンは各ステップの視点を記録します。
5.  操作が完了したら、**「記録停止 (Stop Recording)」** をクリックします。
6.  **「再生 (Play)」** をクリックしてプレビューします。

### 高度な編集と設定
録画後、リストを使って各ステップを詳細に調整できます：

#### 1. ステップ管理
*   **リストナビゲーション**: リスト内のステップをクリックすると、ビューポートがそのステップの状態とアングルにジャンプします。
*   **削除/再録画**: ステップが気に入らない場合は削除するか、そのステップから「記録」を行って操作を追加できます。

#### 2. カメラ調整
*   **視点のリセット**: 特定のステップで視点が悪い（例：遮られている）場合、リストでそのステップを選択し、ビューポートを調整して **「カメラ位置をリセット (Reset Camera)」** をクリックします。再生時、カメラはこの新しいアングルへ滑らかに移行します。

#### 3. 視覚的マーキング（エッジハイライト）
*   **辺をマーク (Mark Edges)**: チュートリアルで操作した辺を明確にするため、ステップで「辺の表示」を有効にし、「辺をマーク」をクリックして編集モードで特定の辺を選択できます。
*   **スタイル調整**: ハイライトされる辺の色と太さをカスタマイズ可能。
*   **ジオメトリノード対応**: マークされた辺は `New Edge` という属性を生成します。これをジオメトリノード（Geometry Nodes）と組み合わせて、発光ラインやアウトラインなどのカスタムエフェクトを作成できます。

#### 4. タイミング制御（重要な機能）
アニメーションを「カメラ移動」と「メッシュ変形」の2つの部分に分け、それぞれの期間を制御できます：
*   **グローバル設定**:
    *   **カメラ期間**: 前のステップから現在の位置までカメラが移動する時間。
    *   **メッシュ期間**: モデルが前の形状から現在の形状に変形する時間。
    *   *ヒント: 時間を長くすると動作が滑らかになり、短くするとキビキビした動作になります。*
*   **カスタムタイミング (ステップごと)**: ステップの **「カスタムタイミング」** にチェックを入れると、そのステップ専用のカメラとメッシュの期間を設定できます（例：重要なステップはスローモーション、移行部は早送り）。

#### 5. 再生とレンダリング範囲
*   **再生モード**:
    *   **最初から**: ステップ0から最後まで再生。
    *   **アクティブなステップから**: 現在選択されているステップから再生開始。
*   **範囲設定**: **「開始を設定」** と **「終了を設定」** ボタンを使用して、再生/レンダリングする特定の区間を指定できます（例：ステップ3から7のみレンダリング）。

### 書き出しとレンダリング
「出力」パネルには2つの書き出しモードがあります：
*   **ビューポート (Viewport)**: 「ビューポートアニメーションレンダリング」に似ており、高速で見たままの結果が得られます。
*   **レンダリング (Render)**: 現在のレンダーエンジン（Eevee/Cycles）を使用して最終出力を行い、ライティングやマテリアルを反映します。
*   **フォーマット制御**: 出力形式（画像連番または動画）は、Blenderの「出力プロパティ」パネルの設定に依存します。

### 注意事項
*   **Dyntopo**: スカルプトモードでは Dyntopo（ダイナミックトポロジー）を使用しないでください。予測不能な頂点の変化が発生し、補間が失敗します。代わりにリメッシュ（Remesh）を使用してください。
*   **データ保存**: 記録されたすべてのデータ（ステップ、アングル、マーク）は現在の `.blend` ファイルに保存され、次回開いたときに編集を継続できます。

---

## Español

**Shaping Recorder** es un complemento auxiliar diseñado para crear tutoriales de modelado y escultura en Blender. Puede registrar cada deformación de malla, cambio de topología y el ángulo de cámara correspondiente del objeto, y permite reproducir y renderizar estos procesos suavemente.

### Características Principales
*   **Grabación de Proceso Completo**: Soporta cambios de topología en Modo Edición (Extrusión, Biselado, Cortes, etc.) y deformaciones en Modo Escultura (soporta Remesh, **NO soporta Dyntopo/Topología Dinámica**).
*   **Soporte Multi-Objeto**: Puede grabar múltiples objetos diferentes en la escena por separado. Al cambiar el objeto seleccionado se cambian los datos de grabación, los cuales se guardan con el archivo `.blend`.
*   **Reproducción Inteligente**: Genera automáticamente una animación interpolada suave entre pasos.
*   **Ajuste Posterior**: Una vez finalizada la grabación, puede modificar libremente el ángulo de cámara y la duración de cada paso, o incluso eliminar pasos innecesarios sin necesidad de volver a grabar.

### Instalación
1.  Descargue el archivo ZIP del complemento.
2.  En Blender, abra **Editar (Edit) → Preferencias (Preferences) → Complementos (Add-ons)**.
3.  Haga clic en **Instalar (Install)**, seleccione el archivo ZIP y habilite **Shaping Recorder**.
4.  Encuentre el panel del complemento en la Barra Lateral de la Vista 3D (tecla N).

### Flujo de Uso Básico
1.  Seleccione un objeto de malla.
2.  Haga clic en **"Iniciar Grabación" (Start Recording)** en el panel.
3.  Realice operaciones de modelado o escultura (cada operación completada se considera un "paso").
4.  Durante el proceso, puede ajustar el ángulo del visor en cualquier momento; el complemento registra la vista en cada paso.
5.  Al finalizar, haga clic en **"Detener Grabación" (Stop Recording)**.
6.  Haga clic en **"Reproducir" (Play)** para previsualizar.

### Edición Avanzada y Configuración
Tras grabar, puede ajustar cada paso detalladamente a través de la lista:

#### 1. Gestión de Pasos
*   **Navegación**: Al hacer clic en un paso de la lista, el visor saltará al estado y ángulo de ese paso.
*   **Eliminar/Regrabar**: Si un paso no es satisfactorio, puede eliminarlo o continuar añadiendo operaciones desde ese paso mediante "Grabar".

#### 2. Ajuste de Cámara
*   **Restablecer Vista**: Si la vista es mala en un paso (ej. obstruida), selecciónelo en la lista, ajuste el visor y haga clic en **"Restablecer posición de cámara"**. Al reproducir, la cámara transicionará suavemente a este nuevo ángulo.

#### 3. Marcado Visual (Resaltado de Bordes)
*   **Marcar Bordes**: Para mostrar claramente qué bordes se operaron, habilite "Visualización de bordes" en un paso, haga clic en "Marcar borde", entre en Modo Edición y seleccione los bordes.
*   **Ajuste de Estilo**: Soporta color y grosor personalizados para los bordes resaltados.
*   **Soporte de Nodos de Geometría**: Los bordes marcados generan un atributo llamado `New Edge`. Puede usar esto con Geometry Nodes para crear efectos personalizados (ej. líneas brillantes).

#### 4. Control de Tiempo (Característica Clave)
El complemento divide la animación en "Movimiento de Cámara" y "Deformación de Malla", permitiendo controlar la duración por separado:
*   **Configuración Global**:
    *   **Duración de Cámara**: Tiempo para mover la cámara del paso anterior al actual.
    *   **Duración de Malla**: Tiempo para que el modelo cambie de forma.
    *   *Consejo: Aumentar el tiempo suaviza la acción; reducirlo la hace más rápida.*
*   **Tiempo Personalizado (Por Paso)**: Marque **"Usar tiempo personalizado"** en un paso para establecer duraciones de cámara y malla específicas para ese paso.

#### 5. Rango de Reproducción y Renderizado
*   **Modo de Reproducción**:
    *   **Desde el inicio**: Reproduce del paso 0 al final.
    *   **Desde el paso activo**: Reproduce desde el paso seleccionado actualmente.
*   **Configuración de Rango**: Use los botones **"Establecer inicio"** y **"Establecer fin"** para especificar un intervalo (ej. renderizar solo del paso 3 al 7).

### Exportación y Renderizado
El panel "Salida" ofrece dos modos:
*   **Vista (Viewport)**: Rápido, lo que ves es lo que obtienes (OpenGL).
*   **Renderizado (Render)**: Usa el motor actual (Eevee/Cycles) para salida final con luces y materiales.
*   **Formato**: Depende de la configuración en el panel "Propiedades de Salida" de Blender (imagen o video).

### Notas
*   **Dyntopo**: NO use Dyntopo (Topología Dinámica) en Modo Escultura, ya que causa cambios de vértices impredecibles que rompen la interpolación. Use Remesh en su lugar.
*   **Guardado de Datos**: Todos los datos se guardan en el archivo `.blend` actual.

---

## Deutsch

**Shaping Recorder** ist ein Hilfs-Add-on für die Erstellung von Blender Modeling- und Sculpting-Tutorials. Es zeichnet jede Mesh-Verformung, Topologieänderung und den entsprechenden Kamerawinkel auf und ermöglicht eine flüssige Wiedergabe und das Rendern dieser Prozesse.

### Kernfunktionen
*   **Vollständige Prozessaufzeichnung**: Unterstützt Topologieänderungen im Edit Mode (Extrude, Bevel etc.) und Verformungen im Sculpt Mode (unterstützt Remesh, **unterstützt KEIN Dyntopo/Dynamische Topologie**).
*   **Multi-Objekt-Unterstützung**: Sie können mehrere verschiedene Objekte in der Szene separat aufzeichnen. Das Umschalten des ausgewählten Objekts wechselt die Aufzeichnungsdaten, die mit der `.blend`-Datei gespeichert werden.
*   **Intelligente Wiedergabe**: Erzeugt automatisch flüssige Interpolationsanimationen zwischen den Schritten.
*   **Nachträgliche Anpassung**: Nach der Aufnahme können Sie Kamerawinkel und Dauer für jeden Schritt frei ändern oder unnötige Schritte löschen, ohne neu aufnehmen zu müssen.

### Installation
1.  Laden Sie die ZIP-Datei des Add-ons herunter.
2.  Öffnen Sie in Blender **Bearbeiten (Edit) → Einstellungen (Preferences) → Add-ons**.
3.  Klicken Sie auf **Installieren (Install)**, wählen Sie die ZIP-Datei und aktivieren Sie **Shaping Recorder**.
4.  Sie finden das Panel in der 3D-Viewport-Seitenleiste (N-Taste).

### Grundlegender Ablauf
1.  Wählen Sie ein Mesh-Objekt aus.
2.  Klicken Sie im Panel auf **„Aufnahme starten“ (Start Recording)**.
3.  Führen Sie Modeling- oder Sculpting-Operationen durch (jede abgeschlossene Operation gilt als ein „Schritt“).
4.  Während des Vorgangs können Sie den Viewport-Winkel jederzeit anpassen; das Add-on speichert die Ansicht bei jedem Schritt.
5.  Klicken Sie nach Abschluss auf **„Aufnahme stoppen“ (Stop Recording)**.
6.  Klicken Sie auf **„Abspielen“ (Play)** zur Vorschau.

### Erweiterte Bearbeitung & Einstellungen
Nach der Aufnahme können Sie jeden Schritt über die Liste feinjustieren:

#### 1. Schrittverwaltung
*   **Listennavigation**: Ein Klick auf einen Schritt in der Liste springt im Viewport zu dessen Status und Winkel.
*   **Löschen/Neu aufnehmen**: Wenn ein Schritt nicht gefällt, löschen Sie ihn oder fügen Sie über „Aufnahme“ ab diesem Schritt neue Operationen hinzu.

#### 2. Kameraanpassung
*   **Ansicht zurücksetzen**: Wenn die Ansicht bei einem Schritt schlecht ist (z. B. verdeckt), wählen Sie ihn in der Liste, passen den Viewport an und klicken auf **„Kameraposition zurücksetzen“**. Bei der Wiedergabe wechselt die Kamera weich zu diesem neuen Winkel.

#### 3. Visuelle Markierung (Kanten-Hervorhebung)
*   **Kanten markieren**: Um im Tutorial zu zeigen, welche Kanten bearbeitet wurden, aktivieren Sie „Kantenanzeige“, klicken auf „Kante markieren“, wechseln in den Edit Mode und wählen Kanten aus.
*   **Stilanpassung**: Farbe und Dicke der Hervorhebung sind anpassbar.
*   **Geometry Nodes Support**: Markierte Kanten erzeugen ein Attribut namens `New Edge`. Dies kann mit Geometry Nodes für Effekte (z. B. leuchtende Linien) genutzt werden.

#### 4. Zeitsteuerung (Hauptmerkmal)
Das Add-on trennt „Kamerabewegung“ und „Mesh-Verformung“ und erlaubt getrennte Zeitsteuerung:
*   **Globale Einstellungen**:
    *   **Kameradauer**: Zeit für die Kamerabewegung zum aktuellen Schritt.
    *   **Mesh-Dauer**: Zeit für die Formveränderung des Modells.
*   **Benutzerdefiniertes Timing (Pro Schritt)**: Aktivieren Sie **„Benutzerdefiniertes Timing“** für einen Schritt, um spezifische Zeiten festzulegen (z. B. Zeitlupe für wichtige Schritte).

#### 5. Wiedergabe- & Renderbereich
*   **Wiedergabemodus**:
    *   **Vom Start**: Von Schritt 0 bis zum Ende.
    *   **Vom aktiven Schritt**: Startet ab dem aktuell gewählten Schritt.
*   **Bereichseinstellungen**: Nutzen Sie **„Start setzen“** und **„Ende setzen“**, um Intervalle festzulegen (z. B. nur Schritt 3 bis 7 rendern).

### Export & Rendern
Das „Output“-Panel bietet zwei Modi:
*   **Viewport**: Schnell, OpenGL-basiert (WYSIWYG).
*   **Render**: Nutzt die aktuelle Render-Engine (Eevee/Cycles) für finale Qualität mit Licht/Material.
*   **Format**: Hängt von den Blender-Einstellungen unter „Ausgabe“ ab (Bildsequenz oder Video).

### Hinweise
*   **Dyntopo**: Verwenden Sie im Sculpt Mode KEIN Dyntopo, da dies die Interpolation bricht. Nutzen Sie stattdessen Remesh.
*   **Datenspeicherung**: Alle Daten werden in der aktuellen `.blend`-Datei gespeichert.

---

## Français

**Shaping Recorder** est un add-on conçu pour créer des tutoriels vidéo de modélisation et de sculpture sur Blender. Il enregistre chaque déformation de maillage, changement de topologie et angle de caméra correspondant, permettant une lecture et un rendu fluides de ces processus.

### Fonctionnalités Clés
*   **Enregistrement Complet** : Supporte les changements de topologie en Mode Édition (Extrusion, Biseau, etc.) et les déformations en Mode Sculpture (supporte Remesh, **ne supporte PAS Dyntopo/Topologie Dynamique**).
*   **Support Multi-Objets** : Enregistrez plusieurs objets différents dans la scène indépendamment. Les données sont sauvegardées avec le fichier `.blend`.
*   **Lecture Intelligente** : Génère automatiquement une animation interpolée fluide entre les étapes.
*   **Ajustement Postérieur** : Après l'enregistrement, modifiez librement l'angle de caméra et la durée pour chaque étape, ou supprimez des étapes sans réenregistrer.

### Installation
1.  Téléchargez le fichier ZIP.
2.  Dans Blender, allez dans **Édition (Edit) → Préférences (Preferences) → Add-ons**.
3.  Cliquez sur **Installer (Install)**, sélectionnez le ZIP et activez **Shaping Recorder**.
4.  Trouvez le panneau dans la barre latérale de la vue 3D (touche N).

### Utilisation de Base
1.  Sélectionnez un objet maillage.
2.  Cliquez sur **"Démarrer l'enregistrement" (Start Recording)**.
3.  Effectuez des opérations de modélisation ou de sculpture.
4.  Ajustez l'angle de vue à tout moment ; l'add-on enregistre la vue à chaque étape.
5.  Cliquez sur **"Arrêter l'enregistrement" (Stop Recording)** à la fin.
6.  Cliquez sur **"Lire" (Play)** pour prévisualiser.

### Édition Avancée
Après l'enregistrement, ajustez chaque étape via la liste :

#### 1. Gestion des Étapes
*   **Navigation** : Cliquer sur une étape dans la liste place la vue sur l'état de cette étape.
*   **Supprimer/Réenregistrer** : Supprimez une étape insatisfaisante ou continuez l'enregistrement à partir de celle-ci.

#### 2. Ajustement de la Caméra
*   **Réinitialiser la Vue** : Si un angle est mauvais, sélectionnez l'étape, ajustez la vue et cliquez sur **"Réinitialiser la caméra"**. La lecture transitera fluidement vers ce nouvel angle.

#### 3. Marquage Visuel (Arêtes)
*   **Marquer les Arêtes** : Pour montrer les arêtes modifiées, activez "Affichage des arêtes", cliquez sur "Marquer l'arête", et sélectionnez-les en Mode Édition.
*   **Style** : Couleur et épaisseur personnalisables.
*   **Geometry Nodes** : Génère un attribut `New Edge` utilisable dans les Geometry Nodes pour des effets personnalisés.

#### 4. Contrôle du Temps
Séparez "Mouvement Caméra" et "Déformation Maillage" :
*   **Réglages Globaux** : Durée Caméra et Durée Maillage pour toutes les étapes.
*   **Temps Personnalisé** : Cochez **"Utiliser un timing personnalisé"** sur une étape pour définir des durées spécifiques.

#### 5. Plage de Lecture
*   **Modes** : Depuis le début ou Depuis l'étape active.
*   **Plage** : Utilisez **"Définir début"** et **"Définir fin"** pour restreindre la lecture/rendu.

### Export & Rendu
Deux modes dans le panneau "Sortie" :
*   **Viewport** : Rapide (OpenGL).
*   **Rendu** : Utilise le moteur actuel (Eevee/Cycles) pour la qualité finale.
*   **Format** : Dépend des propriétés de sortie de Blender.

### Notes
*   **Dyntopo** : N'utilisez PAS Dyntopo en sculpture (brise l'interpolation). Utilisez Remesh.
*   **Sauvegarde** : Les données sont dans le fichier `.blend`.

---

## Italiano

**Shaping Recorder** è un add-on per creare tutorial di modellazione/scultura in Blender. Registra ogni deformazione della mesh e angolo della telecamera, permettendo una riproduzione fluida.

### Funzionalità Principali
*   **Registrazione Completa**: Supporta Modalità Modifica e Scultura (con Remesh, **NO Dyntopo**).
*   **Multi-Oggetto**: Registra oggetti diversi separatamente. Dati salvati nel `.blend`.
*   **Riproduzione Intelligente**: Interpolazione automatica tra i passi.
*   **Post-Editing**: Modifica angoli camera, durata o elimina passi dopo la registrazione.

### Installazione
1.  Scarica lo ZIP.
2.  Blender: **Modifica → Preferenze → Add-on → Installa**.
3.  Seleziona lo ZIP e abilita **Shaping Recorder**.
4.  Pannello nella barra laterale 3D (tasto N).

### Uso Base
1.  Seleziona mesh.
2.  Clicca **"Avvia registrazione"**.
3.  Modella o scolpisci.
4.  Aggiusta la vista quando vuoi.
5.  Clicca **"Ferma registrazione"**.
6.  Clicca **"Riproduci"**.

### Modifiche Avanzate
#### 1. Gestione Passi
*   Naviga nella lista per vedere gli stati. Elimina o ri-registra passi se necessario.

#### 2. Camera
*   Seleziona un passo, aggiusta la vista e clicca **"Reimposta posizione camera"** per correggere l'angolo.

#### 3. Evidenziazione Bordi
*   Attiva "Visualizzazione bordi", clicca "Segna bordo" e seleziona i bordi in Edit Mode. Genera attributo `New Edge` per Geometry Nodes.

#### 4. Controllo Tempo
*   **Globale**: Imposta durata Camera e Mesh per tutti i passi.
*   **Personalizzato**: Attiva **"Usa tempistiche personalizzate"** su un passo per durate specifiche.

#### 5. Intervallo
*   Imposta inizio/fine riproduzione con i pulsanti **"Imposta inizio/fine"**.

### Export
*   **Viewport**: Veloce (OpenGL).
*   **Render**: Qualità finale (Eevee/Cycles).
*   Formato basato sulle impostazioni di output di Blender.

### Note
*   **Dyntopo**: Non supportato. Usa Remesh.

---

## 한국어

**Shaping Recorder**는 블렌더 모델링/스컬핑 튜토리얼 제작을 위한 보조 애드온입니다. 메쉬 변형, 토폴로지 변경 및 해당 카메라 각도를 기록하여 부드럽게 재생하고 렌더링할 수 있습니다.

### 핵심 기능
*   **전체 과정 기록**: 편집 모드(돌출, 베벨 등) 및 스컬프 모드(Remesh 지원, **Dyntopo/동적 토폴로지 미지원**) 지원.
*   **다중 객체 지원**: 여러 객체를 독립적으로 기록 가능. 데이터는 `.blend` 파일에 저장됨.
*   **스마트 재생**: 단계 간 부드러운 보간 애니메이션 자동 생성.
*   **후편집**: 녹화 후 재녹화 없이 카메라 각도, 시간 수정 및 단계 삭제 가능.

### 설치 방법
1.  ZIP 파일 다운로드.
2.  Blender: **편집 (Edit) → 환경 설정 (Preferences) → 애드온 (Add-ons)**.
3.  **설치 (Install)** 클릭, ZIP 선택 후 **Shaping Recorder** 활성화.
4.  3D 뷰포트 사이드바(N키)에서 패널 확인.

### 기본 사용법
1.  메쉬 객체 선택.
2.  **"기록 시작 (Start Recording)"** 클릭.
3.  모델링/스컬핑 수행 (각 동작이 '단계'로 기록됨).
4.  중간중간 뷰포트 각도 조정 가능.
5.  완료 후 **"기록 중지 (Stop Recording)"** 클릭.
6.  **"재생 (Play)"** 으로 미리보기.

### 고급 편집 및 설정
#### 1. 단계 관리
*   리스트에서 단계를 클릭하여 상태 확인. 삭제하거나 해당 단계부터 이어서 녹화 가능.

#### 2. 카메라 조정
*   특정 단계의 뷰가 좋지 않다면, 뷰포트를 조정하고 **"카메라 위치 재설정"** 클릭. 재생 시 부드럽게 전환됨.

#### 3. 시각적 표시 (엣지 강조)
*   **엣지 표시**: 튜토리얼 명확성을 위해 특정 단계에서 "엣지 표시"를 켜고 "엣지 표시(Mark Edge)"로 엣지 선택.
*   **지오메트리 노드**: `New Edge` 속성을 생성하여 지오메트리 노드에서 특수 효과 제작 가능.

#### 4. 시간 제어
*   **전역 설정**: 모든 단계의 카메라/메쉬 이동 시간 일괄 조정.
*   **사용자 정의 시간**: 특정 단계에 **"사용자 정의 시간 사용"** 체크하여 개별 속도 조절.

#### 5. 범위 설정
*   **"시작 설정"** 및 **"종료 설정"** 버튼으로 특정 구간만 재생/렌더링 가능.

### 내보내기
*   **뷰포트**: 빠른 OpenGL 렌더.
*   **최종 렌더**: Eevee/Cycles를 이용한 고품질 렌더.

### 주의사항
*   **Dyntopo**: 스컬프 모드에서 사용 금지(보간 불가). Remesh 사용 권장.

---

## Polski

**Shaping Recorder** to dodatek pomocniczy do tworzenia tutoriali modelowania i rzeźbienia w Blenderze. Rejestruje deformacje siatki, zmiany topologii oraz kąty kamery, umożliwiając płynne odtwarzanie.

### Główne funkcje
*   **Pełna rejestracja**: Obsługuje Tryb Edycji (Wytłaczanie, Fazowanie itp.) i Tryb Rzeźbienia (wspiera Remesh, **NIE wspiera Dyntopo**).
*   **Wiele obiektów**: Niezależna rejestracja wielu obiektów. Dane zapisywane w pliku `.blend`.
*   **Inteligentne odtwarzanie**: Automatyczna interpolacja między krokami.
*   **Post-edycja**: Możliwość zmiany kątów kamery, czasu trwania i usuwania kroków po nagraniu.

### Instalacja
1.  Pobierz ZIP.
2.  Blender: **Edycja → Preferencje → Dodatki → Zainstaluj**.
3.  Wybierz ZIP i włącz **Shaping Recorder**.

### Użycie
1.  Wybierz obiekt.
2.  Kliknij **"Rozpocznij nagrywanie"**.
3.  Modeluj.
4.  Dostosuj widok w trakcie.
5.  Kliknij **"Zatrzymaj nagrywanie"**.
6.  Kliknij **"Odtwórz"**.

### Edycja
*   **Zarządzanie krokami**: Usuwanie lub dogniywanie od kroku.
*   **Kamera**: Wybierz krok, ustaw widok, kliknij **"Zresetuj pozycję kamery"**.
*   **Podświetlanie krawędzi**: Generuje atrybut `New Edge` dla Geometry Nodes.
*   **Czas**: Ustawienia globalne lub **"Użyj własnego czasu"** dla konkretnego kroku.
*   **Zakres**: Ustaw start/koniec odtwarzania.

### Eksport
*   **Viewport**: Szybki podgląd.
*   **Render**: Finalna jakość (Eevee/Cycles).

---

## Português (Brasil)

**Shaping Recorder** é um add-on auxiliar projetado para criar tutoriais de modelagem e escultura no Blender. Ele registra cada deformação de malha e ângulo de câmera, permitindo reprodução e renderização suaves.

### Recursos Principais
*   **Gravação Completa**: Suporta Modo de Edição e Modo de Escultura (suporta Remesh, **NÃO suporta Dyntopo**).
*   **Múltiplos Objetos**: Grave objetos diferentes independentemente. Dados salvos no `.blend`.
*   **Reprodução Inteligente**: Interpolação automática entre passos.
*   **Pós-Edição**: Modifique ângulos de câmera, duração ou exclua passos após a gravação.

### Instalação
1.  Baixe o ZIP.
2.  Blender: **Edit → Preferences → Add-ons → Install**.
3.  Selecione o ZIP e habilite **Shaping Recorder**.

### Uso Básico
1.  Selecione a malha.
2.  Clique em **"Iniciar gravação"**.
3.  Modele ou esculpa.
4.  Ajuste a viewport durante o processo.
5.  Clique em **"Parar gravação"**.
6.  Clique em **"Reproduzir"**.

### Edição Avançada
*   **Passos**: Navegue, exclua ou continue gravando a partir de um passo.
*   **Câmera**: Ajuste a vista e clique em **"Redefinir posição da câmera"** para corrigir o ângulo.
*   **Arestas**: Use "Marcar aresta" para destaque. Gera atributo `New Edge` para Geometry Nodes.
*   **Tempo**: Controle global ou **"Usar tempo personalizado"** por passo.
*   **Faixa**: Defina início/fim de reprodução.

### Exportação
*   **Viewport**: Rápido (OpenGL).
*   **Render**: Qualidade final (Eevee/Cycles).

---

## Português (Portugal)

**Shaping Recorder** é um add-on auxiliar desenhado para criar tutoriais de modelação e escultura no Blender. Regista cada deformação de malha e ângulo de câmara, permitindo reprodução e renderização suaves.

### Funcionalidades Principais
*   **Gravação Completa**: Suporta Modo de Edição e Modo de Escultura (suporta Remesh, **NÃO suporta Dyntopo**).
*   **Múltiplos Objetos**: Grave objetos diferentes independentemente. Dados guardados no `.blend`.
*   **Reprodução Inteligente**: Interpolação automática entre passos.
*   **Pós-Edição**: Modifique ângulos de câmara, duração ou elimine passos após a gravação.

### Instalação
1.  Descarregue o ZIP.
2.  Blender: **Edit → Preferences → Add-ons → Install**.
3.  Selecione o ZIP e ative **Shaping Recorder**.

### Uso Básico
1.  Selecione a malha.
2.  Clique em **"Iniciar gravação"**.
3.  Modele ou esculpa.
4.  Ajuste o viewport durante o processo.
5.  Clique em **"Parar gravação"**.
6.  Clique em **"Reproduzir"**.

### Edição Avançada
*   **Passos**: Navegue, elimine ou continue a gravar a partir de um passo.
*   **Câmara**: Ajuste a vista e clique em **"Repor posição da câmara"**.
*   **Arestas**: Use "Marcar aresta". Gera atributo `New Edge` para Geometry Nodes.
*   **Tempo**: Controlo global ou **"Usar temporização personalizada"** por passo.
*   **Intervalo**: Defina início/fim de reprodução.

---

## Русский

**Shaping Recorder** — это вспомогательный аддон для создания уроков по моделированию и скульптингу в Blender. Он записывает каждый шаг деформации меша, изменения топологии и соответствующий угол камеры, позволяя плавно воспроизводить и рендерить эти процессы.

### Основные возможности
*   **Полная запись**: Поддержка режима редактирования и режима скульптинга (поддерживает Remesh, **НЕ поддерживает Dyntopo/Динамическую топологию**).
*   **Мульти-объектность**: Запись разных объектов независимо. Данные сохраняются в `.blend`.
*   **Умное воспроизведение**: Автоматическая плавная интерполяция между шагами.
*   **Постредактирование**: Изменение углов камеры, длительности и удаление шагов после записи без перезаписи.

### Установка
1.  Скачайте ZIP.
2.  Blender: **Edit → Preferences → Add-ons → Install**.
3.  Выберите ZIP и включите **Shaping Recorder**.

### Использование
1.  Выберите меш.
2.  Нажмите **"Начать запись" (Start Recording)**.
3.  Моделируйте.
4.  Регулируйте вьюпорт в процессе.
5.  Нажмите **"Остановить запись" (Stop Recording)**.
6.  Нажмите **"Воспроизведение" (Play)**.

### Редактирование
*   **Шаги**: Навигация, удаление или дозапись с шага.
*   **Камера**: Настройте вид и нажмите **"Сбросить позицию камеры"** для исправления угла.
*   **Выделение рёбер**: Функция "Отметить ребро". Создает атрибут `New Edge` для Геометрических Нод.
*   **Время**: Глобальные настройки или **"Использовать свое время"** для отдельного шага.
*   **Диапазон**: Кнопки "Установить начало/конец".

### Экспорт
*   **Viewport**: Быстро (OpenGL).
*   **Render**: Финальное качество (Eevee/Cycles).

### Примечания
*   **Dyntopo**: Не используйте в скульптинге, ломает интерполяцию.

---

## Українська

**Shaping Recorder** — це допоміжний аддон для створення уроків з моделювання та скульптингу в Blender. Він записує кожен крок деформації сітки та кут камери, дозволяючи плавно відтворювати та рендерити ці процеси.

### Основні можливості
*   **Повний запис**: Підтримка режиму редагування та скульптингу (підтримує Remesh, **НЕ підтримує Dyntopo**).
*   **Мульти-об'єктність**: Незалежний запис різних об'єктів. Дані зберігаються у `.blend`.
*   **Розумне відтворення**: Автоматична плавна інтерполяція.
*   **Постредагування**: Зміна кутів камери, тривалості та видалення кроків після запису.

### Встановлення
1.  Завантажте ZIP.
2.  Blender: **Edit → Preferences → Add-ons → Install**.
3.  Виберіть ZIP і увімкніть **Shaping Recorder**.

### Використання
1.  Виберіть сітку.
2.  Натисніть **"Почати запис"**.
3.  Моделюйте.
4.  Регулюйте в'юпорт.
5.  Натисніть **"Зупинити запис"**.
6.  Натисніть **"Відтворення"**.

### Редагування
*   **Кроки**: Навігація, видалення або дозапис.
*   **Камера**: Налаштуйте вид і натисніть **"Скинути позицію камери"**.
*   **Виділення ребер**: Створює атрибут `New Edge` для Геометричних Нод.
*   **Час**: Глобально або **"Використовувати власний час"** для кроку.
*   **Діапазон**: Встановіть початок/кінець.

### Експорт
*   **Viewport**: Швидко.
*   **Render**: Фінальна якість.
