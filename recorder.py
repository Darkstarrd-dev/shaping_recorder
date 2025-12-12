import os
from array import array

import bmesh
import bpy
from bpy.app.translations import pgettext_iface as iface_
from mathutils import kdtree

translations = {
    "zh_HANS": {
        ("*", "Shaping Recorder"): "形变记录器",
        ("*", "Steps: {n}"): "步骤: {n}",
        ("*", "Start Recording"): "开始录制",
        ("*", "Stop Recording"): "停止录制",
        ("Property", "Step Duration"): "步长时间",
        ("Property", "Seconds between steps"): "每步之间的秒数",
        ("Property", "Interpolation Steps"): "插值步数",
        ("Property", "Interpolation frames per step"): "每步插值帧数",
        ("*", "Replay Range (1..{n})"): "回放范围 (1..{n})",
        ("Property", "Start Step"): "起始步",
        (
            "Property",
            "First recorded step to replay (1-based)",
        ): "回放的第一步（从1开始）",
        ("Property", "End Step"): "结束步",
        (
            "Property",
            "Last recorded step to replay (1-based, 0 = to end)",
        ): "回放的最后一步（从1开始，0表示到末尾）",
        ("*", "Frame Export (Sequence)"): "帧导出（序列）",
        ("Property", "File Prefix"): "文件前缀",
        ("Property", "Frame file prefix"): "导出帧文件名前缀",
        ("Property", "Export Render Mode"): "导出渲染模式",
        ("Property", "How to render frames when recording"): "录制导出时使用的渲染方式",
        ("*", "Viewport"): "视口",
        ("*", "Use OpenGL viewport render"): "使用视口 OpenGL 渲染",
        ("*", "Final Render"): "最终渲染",
        ("*", "Use scene render engine"): "使用场景渲染器",
        (
            "*",
            "Uses Output Path directory from Render Properties.",
        ): "使用渲染属性中的输出路径目录。",
        ("*", "Record"): "录制",
        ("*", "Play"): "播放",
        ("*", "Stop"): "停止",
        ("Operator", "Start Recording"): "开始录制",
        ("Operator", "Stop Recording"): "停止录制",
        ("Operator", "Play"): "播放",
        ("Operator", "Stop"): "停止",
        ("Operator", "Record Frames"): "录制帧",
        ("Operator", "Stop Playing"): "停止播放",
    },
    "zh_HANT": {
        ("*", "Shaping Recorder"): "形變記錄器",
        ("*", "Steps: {n}"): "步驟: {n}",
        ("*", "Start Recording"): "開始錄製",
        ("*", "Stop Recording"): "停止錄製",
        ("Property", "Step Duration"): "步長時間",
        ("Property", "Seconds between steps"): "每步之間的秒數",
        ("Property", "Interpolation Steps"): "插值步數",
        ("Property", "Interpolation frames per step"): "每步插值幀數",
        ("*", "Replay Range (1..{n})"): "回放範圍 (1..{n})",
        ("Property", "Start Step"): "起始步",
        ("Property", "First recorded step to replay (1-based)"): "回放的第一步（從1開始）",
        ("Property", "End Step"): "結束步",
        ("Property", "Last recorded step to replay (1-based, 0 = to end)"): "回放的最後一步（從1開始，0表示到末尾）",
        ("*", "Frame Export (Sequence)"): "幀匯出（序列）",
        ("Property", "File Prefix"): "檔案前綴",
        ("Property", "Frame file prefix"): "匯出幀檔案名前綴",
        ("Property", "Export Render Mode"): "匯出渲染模式",
        ("Property", "How to render frames when recording"): "錄製匯出時使用的渲染方式",
        ("*", "Viewport"): "視口",
        ("*", "Use OpenGL viewport render"): "使用視口 OpenGL 渲染",
        ("*", "Final Render"): "最終渲染",
        ("*", "Use scene render engine"): "使用場景渲染器",
        ("*", "Uses Output Path directory from Render Properties."): "使用渲染屬性中的輸出路徑目錄。",
        ("*", "Record"): "錄製",
        ("*", "Play"): "播放",
        ("*", "Stop"): "停止",
        ("Operator", "Start Recording"): "開始錄製",
        ("Operator", "Stop Recording"): "停止錄製",
        ("Operator", "Play"): "播放",
        ("Operator", "Stop"): "停止",
        ("Operator", "Record Frames"): "錄製幀",
        ("Operator", "Stop Playing"): "停止播放",
    },
    "ja_JP": {
        ("*", "Shaping Recorder"): "シェイピングレコーダー",
        ("*", "Steps: {n}"): "ステップ: {n}",
        ("*", "Start Recording"): "記録開始",
        ("*", "Stop Recording"): "記録停止",
        ("Property", "Step Duration"): "ステップ間隔",
        ("Property", "Seconds between steps"): "ステップ間の秒数",
        ("Property", "Interpolation Steps"): "補間ステップ",
        ("Property", "Interpolation frames per step"): "ステップごとの補間フレーム数",
        ("*", "Replay Range (1..{n})"): "再生範囲 (1..{n})",
        ("Property", "Start Step"): "開始ステップ",
        (
            "Property",
            "First recorded step to replay (1-based)",
        ): "再生開始ステップ（1始まり）",
        ("Property", "End Step"): "終了ステップ",
        (
            "Property",
            "Last recorded step to replay (1-based, 0 = to end)",
        ): "再生終了ステップ（1始まり、0で最後まで）",
        ("*", "Frame Export (Sequence)"): "フレーム書き出し（連番）",
        ("Property", "File Prefix"): "ファイル接頭辞",
        ("Property", "Frame file prefix"): "書き出しフレームの接頭辞",
        ("Property", "Export Render Mode"): "書き出しレンダーモード",
        (
            "Property",
            "How to render frames when recording",
        ): "記録時のフレームレンダリング方法",
        ("*", "Viewport"): "ビューポート",
        ("*", "Use OpenGL viewport render"): "OpenGL ビューポートレンダーを使用",
        ("*", "Final Render"): "最終レンダー",
        ("*", "Use scene render engine"): "シーンのレンダーエンジンを使用",
        (
            "*",
            "Uses Output Path directory from Render Properties.",
        ): "レンダープロパティの出力パスを使用します。",
        ("*", "Record"): "書き出し",
        ("*", "Play"): "再生",
        ("*", "Stop"): "停止",
        ("Operator", "Start Recording"): "記録開始",
        ("Operator", "Stop Recording"): "記録停止",
        ("Operator", "Play"): "再生",
        ("Operator", "Stop"): "停止",
        ("Operator", "Record Frames"): "フレームを書き出し",
        ("Operator", "Stop Playing"): "再生停止",
    },
    "es": {
        ("*", "Shaping Recorder"): "Grabador de Modelado",
        ("*", "Steps: {n}"): "Pasos: {n}",
        ("*", "Start Recording"): "Iniciar grabación",
        ("*", "Stop Recording"): "Detener grabación",
        ("Property", "Step Duration"): "Duración de paso",
        ("Property", "Seconds between steps"): "Segundos entre pasos",
        ("Property", "Interpolation Steps"): "Pasos de interpolación",
        (
            "Property",
            "Interpolation frames per step",
        ): "Fotogramas de interpolación por paso",
        ("*", "Replay Range (1..{n})"): "Rango de reproducción (1..{n})",
        ("Property", "Start Step"): "Paso inicial",
        (
            "Property",
            "First recorded step to replay (1-based)",
        ): "Primer paso a reproducir (desde 1)",
        ("Property", "End Step"): "Paso final",
        (
            "Property",
            "Last recorded step to replay (1-based, 0 = to end)",
        ): "Último paso a reproducir (desde 1, 0 = hasta el final)",
        ("*", "Frame Export (Sequence)"): "Exportación de fotogramas (secuencia)",
        ("Property", "File Prefix"): "Prefijo de archivo",
        ("Property", "Frame file prefix"): "Prefijo para archivos de fotogramas",
        ("Property", "Export Render Mode"): "Modo de render para exportar",
        (
            "Property",
            "How to render frames when recording",
        ): "Cómo renderizar fotogramas al grabar",
        ("*", "Viewport"): "Vista",
        ("*", "Use OpenGL viewport render"): "Usar render OpenGL del visor",
        ("*", "Final Render"): "Render final",
        ("*", "Use scene render engine"): "Usar el motor de render de la escena",
        (
            "*",
            "Uses Output Path directory from Render Properties.",
        ): "Usa el directorio de ruta de salida en Propiedades de Render.",
        ("*", "Record"): "Grabar",
        ("*", "Play"): "Reproducir",
        ("*", "Stop"): "Detener",
        ("Operator", "Start Recording"): "Iniciar grabación",
        ("Operator", "Stop Recording"): "Detener grabación",
        ("Operator", "Play"): "Reproducir",
        ("Operator", "Stop"): "Detener",
        ("Operator", "Record Frames"): "Grabar fotogramas",
        ("Operator", "Stop Playing"): "Detener reproducción",
    },
    "de_DE": {
        ("*", "Shaping Recorder"): "Formrecorder",
        ("*", "Steps: {n}"): "Schritte: {n}",
        ("*", "Start Recording"): "Aufnahme starten",
        ("*", "Stop Recording"): "Aufnahme stoppen",
        ("Property", "Step Duration"): "Schrittdauer",
        ("Property", "Seconds between steps"): "Sekunden zwischen Schritten",
        ("Property", "Interpolation Steps"): "Interpolationsschritte",
        ("Property", "Interpolation frames per step"): "Interpolationsbilder pro Schritt",
        ("*", "Replay Range (1..{n})"): "Wiedergabebereich (1..{n})",
        ("Property", "Start Step"): "Startschritt",
        ("Property", "First recorded step to replay (1-based)"): "Erster wiederzugebender Schritt (ab 1)",
        ("Property", "End Step"): "Endschritt",
        ("Property", "Last recorded step to replay (1-based, 0 = to end)"): "Letzter wiederzugebender Schritt (ab 1, 0 = bis zum Ende)",
        ("*", "Frame Export (Sequence)"): "Frame-Export (Sequenz)",
        ("Property", "File Prefix"): "Dateipräfix",
        ("Property", "Frame file prefix"): "Präfix für Frame-Dateien",
        ("Property", "Export Render Mode"): "Export-Rendermodus",
        ("Property", "How to render frames when recording"): "Wie Frames beim Export gerendert werden",
        ("*", "Viewport"): "Viewport",
        ("*", "Use OpenGL viewport render"): "OpenGL-Viewport-Render verwenden",
        ("*", "Final Render"): "Finales Rendern",
        ("*", "Use scene render engine"): "Szenen-Render-Engine verwenden",
        ("*", "Uses Output Path directory from Render Properties."): "Verwendet das Ausgabeverzeichnis aus den Render-Eigenschaften.",
        ("*", "Record"): "Aufnehmen",
        ("*", "Play"): "Abspielen",
        ("*", "Stop"): "Stopp",
        ("Operator", "Start Recording"): "Aufnahme starten",
        ("Operator", "Stop Recording"): "Aufnahme stoppen",
        ("Operator", "Play"): "Abspielen",
        ("Operator", "Stop"): "Stopp",
        ("Operator", "Record Frames"): "Frames aufnehmen",
        ("Operator", "Stop Playing"): "Wiedergabe stoppen",
    },
    "fr_FR": {
        ("*", "Shaping Recorder"): "Enregistreur de Forme",
        ("*", "Steps: {n}"): "Étapes : {n}",
        ("*", "Start Recording"): "Démarrer l'enregistrement",
        ("*", "Stop Recording"): "Arrêter l'enregistrement",
        ("Property", "Step Duration"): "Durée de l'étape",
        ("Property", "Seconds between steps"): "Secondes entre les étapes",
        ("Property", "Interpolation Steps"): "Étapes d'interpolation",
        ("Property", "Interpolation frames per step"): "Images d'interpolation par étape",
        ("*", "Replay Range (1..{n})"): "Plage de lecture (1..{n})",
        ("Property", "Start Step"): "Étape de début",
        ("Property", "First recorded step to replay (1-based)"): "Première étape à lire (à partir de 1)",
        ("Property", "End Step"): "Étape de fin",
        ("Property", "Last recorded step to replay (1-based, 0 = to end)"): "Dernière étape à lire (à partir de 1, 0 = jusqu'à la fin)",
        ("*", "Frame Export (Sequence)"): "Export d'images (séquence)",
        ("Property", "File Prefix"): "Préfixe de fichier",
        ("Property", "Frame file prefix"): "Préfixe des fichiers d'images",
        ("Property", "Export Render Mode"): "Mode de rendu d'export",
        ("Property", "How to render frames when recording"): "Comment rendre les images lors de l'enregistrement",
        ("*", "Viewport"): "Vue",
        ("*", "Use OpenGL viewport render"): "Utiliser le rendu OpenGL de la vue",
        ("*", "Final Render"): "Rendu final",
        ("*", "Use scene render engine"): "Utiliser le moteur de rendu de la scène",
        ("*", "Uses Output Path directory from Render Properties."): "Utilise le répertoire du chemin de sortie des propriétés de rendu.",
        ("*", "Record"): "Enregistrer",
        ("*", "Play"): "Lire",
        ("*", "Stop"): "Arrêter",
        ("Operator", "Start Recording"): "Démarrer l'enregistrement",
        ("Operator", "Stop Recording"): "Arrêter l'enregistrement",
        ("Operator", "Play"): "Lire",
        ("Operator", "Stop"): "Arrêter",
        ("Operator", "Record Frames"): "Enregistrer des images",
        ("Operator", "Stop Playing"): "Arrêter la lecture",
    },
    "it_IT": {
        ("*", "Shaping Recorder"): "Registratore di Modellazione",
        ("*", "Steps: {n}"): "Passi: {n}",
        ("*", "Start Recording"): "Avvia registrazione",
        ("*", "Stop Recording"): "Ferma registrazione",
        ("Property", "Step Duration"): "Durata passo",
        ("Property", "Seconds between steps"): "Secondi tra i passi",
        ("Property", "Interpolation Steps"): "Passi di interpolazione",
        ("Property", "Interpolation frames per step"): "Fotogrammi di interpolazione per passo",
        ("*", "Replay Range (1..{n})"): "Intervallo riproduzione (1..{n})",
        ("Property", "Start Step"): "Passo iniziale",
        ("Property", "First recorded step to replay (1-based)"): "Primo passo da riprodurre (da 1)",
        ("Property", "End Step"): "Passo finale",
        ("Property", "Last recorded step to replay (1-based, 0 = to end)"): "Ultimo passo da riprodurre (da 1, 0 = fino alla fine)",
        ("*", "Frame Export (Sequence)"): "Esportazione fotogrammi (sequenza)",
        ("Property", "File Prefix"): "Prefisso file",
        ("Property", "Frame file prefix"): "Prefisso dei file fotogramma",
        ("Property", "Export Render Mode"): "Modalità di render esportazione",
        ("Property", "How to render frames when recording"): "Come renderizzare i fotogrammi durante la registrazione",
        ("*", "Viewport"): "Viewport",
        ("*", "Use OpenGL viewport render"): "Usa render OpenGL del viewport",
        ("*", "Final Render"): "Render finale",
        ("*", "Use scene render engine"): "Usa il motore di render della scena",
        ("*", "Uses Output Path directory from Render Properties."): "Usa la cartella del percorso di output dalle Proprietà di Render.",
        ("*", "Record"): "Registra",
        ("*", "Play"): "Riproduci",
        ("*", "Stop"): "Ferma",
        ("Operator", "Start Recording"): "Avvia registrazione",
        ("Operator", "Stop Recording"): "Ferma registrazione",
        ("Operator", "Play"): "Riproduci",
        ("Operator", "Stop"): "Ferma",
        ("Operator", "Record Frames"): "Registra fotogrammi",
        ("Operator", "Stop Playing"): "Ferma riproduzione",
    },
    "ko_KR": {
        ("*", "Shaping Recorder"): "형상 기록기",
        ("*", "Steps: {n}"): "단계: {n}",
        ("*", "Start Recording"): "기록 시작",
        ("*", "Stop Recording"): "기록 중지",
        ("Property", "Step Duration"): "단계 지속 시간",
        ("Property", "Seconds between steps"): "단계 간 초",
        ("Property", "Interpolation Steps"): "보간 단계",
        ("Property", "Interpolation frames per step"): "단계당 보간 프레임 수",
        ("*", "Replay Range (1..{n})"): "재생 범위 (1..{n})",
        ("Property", "Start Step"): "시작 단계",
        ("Property", "First recorded step to replay (1-based)"): "재생할 첫 단계(1부터)",
        ("Property", "End Step"): "끝 단계",
        ("Property", "Last recorded step to replay (1-based, 0 = to end)"): "재생할 마지막 단계(1부터, 0=끝까지)",
        ("*", "Frame Export (Sequence)"): "프레임 내보내기(시퀀스)",
        ("Property", "File Prefix"): "파일 접두사",
        ("Property", "Frame file prefix"): "프레임 파일 접두사",
        ("Property", "Export Render Mode"): "내보내기 렌더 모드",
        ("Property", "How to render frames when recording"): "기록 시 프레임 렌더 방식",
        ("*", "Viewport"): "뷰포트",
        ("*", "Use OpenGL viewport render"): "OpenGL 뷰포트 렌더 사용",
        ("*", "Final Render"): "최종 렌더",
        ("*", "Use scene render engine"): "장면 렌더 엔진 사용",
        ("*", "Uses Output Path directory from Render Properties."): "렌더 속성의 출력 경로 폴더를 사용합니다.",
        ("*", "Record"): "기록",
        ("*", "Play"): "재생",
        ("*", "Stop"): "정지",
        ("Operator", "Start Recording"): "기록 시작",
        ("Operator", "Stop Recording"): "기록 중지",
        ("Operator", "Play"): "재생",
        ("Operator", "Stop"): "정지",
        ("Operator", "Record Frames"): "프레임 기록",
        ("Operator", "Stop Playing"): "재생 중지",
    },
    "pl_PL": {
        ("*", "Shaping Recorder"): "Rejestrator Kształtowania",
        ("*", "Steps: {n}"): "Kroki: {n}",
        ("*", "Start Recording"): "Rozpocznij nagrywanie",
        ("*", "Stop Recording"): "Zatrzymaj nagrywanie",
        ("Property", "Step Duration"): "Czas kroku",
        ("Property", "Seconds between steps"): "Sekundy między krokami",
        ("Property", "Interpolation Steps"): "Kroki interpolacji",
        ("Property", "Interpolation frames per step"): "Klatki interpolacji na krok",
        ("*", "Replay Range (1..{n})"): "Zakres odtwarzania (1..{n})",
        ("Property", "Start Step"): "Krok początkowy",
        ("Property", "First recorded step to replay (1-based)"): "Pierwszy krok do odtworzenia (od 1)",
        ("Property", "End Step"): "Krok końcowy",
        ("Property", "Last recorded step to replay (1-based, 0 = to end)"): "Ostatni krok do odtworzenia (od 1, 0 = do końca)",
        ("*", "Frame Export (Sequence)"): "Eksport klatek (sekwencja)",
        ("Property", "File Prefix"): "Prefiks pliku",
        ("Property", "Frame file prefix"): "Prefiks nazw plików klatek",
        ("Property", "Export Render Mode"): "Tryb renderu eksportu",
        ("Property", "How to render frames when recording"): "Sposób renderowania klatek podczas nagrywania",
        ("*", "Viewport"): "Widok",
        ("*", "Use OpenGL viewport render"): "Użyj renderu OpenGL widoku",
        ("*", "Final Render"): "Render końcowy",
        ("*", "Use scene render engine"): "Użyj silnika renderu sceny",
        ("*", "Uses Output Path directory from Render Properties."): "Używa folderu ścieżki wyjścia z Właściwości Renderu.",
        ("*", "Record"): "Nagrywaj",
        ("*", "Play"): "Odtwórz",
        ("*", "Stop"): "Zatrzymaj",
        ("Operator", "Start Recording"): "Rozpocznij nagrywanie",
        ("Operator", "Stop Recording"): "Zatrzymaj nagrywanie",
        ("Operator", "Play"): "Odtwórz",
        ("Operator", "Stop"): "Zatrzymaj",
        ("Operator", "Record Frames"): "Nagrywaj klatki",
        ("Operator", "Stop Playing"): "Zatrzymaj odtwarzanie",
    },
    "pt_BR": {
        ("*", "Shaping Recorder"): "Gravador de Modelagem",
        ("*", "Steps: {n}"): "Passos: {n}",
        ("*", "Start Recording"): "Iniciar gravação",
        ("*", "Stop Recording"): "Parar gravação",
        ("Property", "Step Duration"): "Duração do passo",
        ("Property", "Seconds between steps"): "Segundos entre passos",
        ("Property", "Interpolation Steps"): "Passos de interpolação",
        ("Property", "Interpolation frames per step"): "Quadros de interpolação por passo",
        ("*", "Replay Range (1..{n})"): "Intervalo de reprodução (1..{n})",
        ("Property", "Start Step"): "Passo inicial",
        ("Property", "First recorded step to replay (1-based)"): "Primeiro passo a reproduzir (a partir de 1)",
        ("Property", "End Step"): "Passo final",
        ("Property", "Last recorded step to replay (1-based, 0 = to end)"): "Último passo a reproduzir (a partir de 1, 0 = até o fim)",
        ("*", "Frame Export (Sequence)"): "Exportação de quadros (sequência)",
        ("Property", "File Prefix"): "Prefixo de arquivo",
        ("Property", "Frame file prefix"): "Prefixo do arquivo de quadros",
        ("Property", "Export Render Mode"): "Modo de render para exportação",
        ("Property", "How to render frames when recording"): "Como renderizar quadros ao gravar",
        ("*", "Viewport"): "Viewport",
        ("*", "Use OpenGL viewport render"): "Usar render OpenGL do viewport",
        ("*", "Final Render"): "Render final",
        ("*", "Use scene render engine"): "Usar o motor de render da cena",
        ("*", "Uses Output Path directory from Render Properties."): "Usa o diretório do Caminho de Saída nas Propriedades de Render.",
        ("*", "Record"): "Gravar",
        ("*", "Play"): "Reproduzir",
        ("*", "Stop"): "Parar",
        ("Operator", "Start Recording"): "Iniciar gravação",
        ("Operator", "Stop Recording"): "Parar gravação",
        ("Operator", "Play"): "Reproduzir",
        ("Operator", "Stop"): "Parar",
        ("Operator", "Record Frames"): "Gravar quadros",
        ("Operator", "Stop Playing"): "Parar reprodução",
    },
    "pt_PT": {
        ("*", "Shaping Recorder"): "Gravador de Modelação",
        ("*", "Steps: {n}"): "Passos: {n}",
        ("*", "Start Recording"): "Iniciar gravação",
        ("*", "Stop Recording"): "Parar gravação",
        ("Property", "Step Duration"): "Duração do passo",
        ("Property", "Seconds between steps"): "Segundos entre passos",
        ("Property", "Interpolation Steps"): "Passos de interpolação",
        ("Property", "Interpolation frames per step"): "Fotogramas de interpolação por passo",
        ("*", "Replay Range (1..{n})"): "Intervalo de reprodução (1..{n})",
        ("Property", "Start Step"): "Passo inicial",
        ("Property", "First recorded step to replay (1-based)"): "Primeiro passo a reproduzir (a partir de 1)",
        ("Property", "End Step"): "Passo final",
        ("Property", "Last recorded step to replay (1-based, 0 = to end)"): "Último passo a reproduzir (a partir de 1, 0 = até ao fim)",
        ("*", "Frame Export (Sequence)"): "Exportação de fotogramas (sequência)",
        ("Property", "File Prefix"): "Prefixo de ficheiro",
        ("Property", "Frame file prefix"): "Prefixo dos ficheiros de fotogramas",
        ("Property", "Export Render Mode"): "Modo de renderização de exportação",
        ("Property", "How to render frames when recording"): "Como renderizar fotogramas ao gravar",
        ("*", "Viewport"): "Viewport",
        ("*", "Use OpenGL viewport render"): "Usar render OpenGL do viewport",
        ("*", "Final Render"): "Render final",
        ("*", "Use scene render engine"): "Usar o motor de renderização da cena",
        ("*", "Uses Output Path directory from Render Properties."): "Usa o diretório do Caminho de Saída nas Propriedades de Renderização.",
        ("*", "Record"): "Gravar",
        ("*", "Play"): "Reproduzir",
        ("*", "Stop"): "Parar",
        ("Operator", "Start Recording"): "Iniciar gravação",
        ("Operator", "Stop Recording"): "Parar gravação",
        ("Operator", "Play"): "Reproduzir",
        ("Operator", "Stop"): "Parar",
        ("Operator", "Record Frames"): "Gravar fotogramas",
        ("Operator", "Stop Playing"): "Parar reprodução",
    },
    "ru_RU": {
        ("*", "Shaping Recorder"): "Запись Формы",
        ("*", "Steps: {n}"): "Шаги: {n}",
        ("*", "Start Recording"): "Начать запись",
        ("*", "Stop Recording"): "Остановить запись",
        ("Property", "Step Duration"): "Длительность шага",
        ("Property", "Seconds between steps"): "Секунд между шагами",
        ("Property", "Interpolation Steps"): "Шаги интерполяции",
        ("Property", "Interpolation frames per step"): "Интерполяционных кадров на шаг",
        ("*", "Replay Range (1..{n})"): "Диапазон воспроизведения (1..{n})",
        ("Property", "Start Step"): "Начальный шаг",
        ("Property", "First recorded step to replay (1-based)"): "Первый шаг для воспроизведения (с 1)",
        ("Property", "End Step"): "Конечный шаг",
        ("Property", "Last recorded step to replay (1-based, 0 = to end)"): "Последний шаг для воспроизведения (с 1, 0 = до конца)",
        ("*", "Frame Export (Sequence)"): "Экспорт кадров (последовательность)",
        ("Property", "File Prefix"): "Префикс файла",
        ("Property", "Frame file prefix"): "Префикс файлов кадров",
        ("Property", "Export Render Mode"): "Режим рендера экспорта",
        ("Property", "How to render frames when recording"): "Как рендерить кадры при записи",
        ("*", "Viewport"): "Окно просмотра",
        ("*", "Use OpenGL viewport render"): "Использовать OpenGL-рендер окна просмотра",
        ("*", "Final Render"): "Финальный рендер",
        ("*", "Use scene render engine"): "Использовать движок рендера сцены",
        ("*", "Uses Output Path directory from Render Properties."): "Использует каталог пути вывода из свойств рендера.",
        ("*", "Record"): "Запись",
        ("*", "Play"): "Воспроизвести",
        ("*", "Stop"): "Стоп",
        ("Operator", "Start Recording"): "Начать запись",
        ("Operator", "Stop Recording"): "Остановить запись",
        ("Operator", "Play"): "Воспроизвести",
        ("Operator", "Stop"): "Стоп",
        ("Operator", "Record Frames"): "Записать кадры",
        ("Operator", "Stop Playing"): "Остановить воспроизведение",
    },
    "uk_UA": {
        ("*", "Shaping Recorder"): "Запис Формування",
        ("*", "Steps: {n}"): "Кроки: {n}",
        ("*", "Start Recording"): "Почати запис",
        ("*", "Stop Recording"): "Зупинити запис",
        ("Property", "Step Duration"): "Тривалість кроку",
        ("Property", "Seconds between steps"): "Секунд між кроками",
        ("Property", "Interpolation Steps"): "Кроки інтерполяції",
        ("Property", "Interpolation frames per step"): "Інтерполяційних кадрів на крок",
        ("*", "Replay Range (1..{n})"): "Діапазон відтворення (1..{n})",
        ("Property", "Start Step"): "Початковий крок",
        ("Property", "First recorded step to replay (1-based)"): "Перший крок для відтворення (з 1)",
        ("Property", "End Step"): "Кінцевий крок",
        ("Property", "Last recorded step to replay (1-based, 0 = to end)"): "Останній крок для відтворення (з 1, 0 = до кінця)",
        ("*", "Frame Export (Sequence)"): "Експорт кадрів (послідовність)",
        ("Property", "File Prefix"): "Префікс файлу",
        ("Property", "Frame file prefix"): "Префікс файлів кадрів",
        ("Property", "Export Render Mode"): "Режим рендера експорту",
        ("Property", "How to render frames when recording"): "Як рендерити кадри під час запису",
        ("*", "Viewport"): "В'юпорт",
        ("*", "Use OpenGL viewport render"): "Використовувати OpenGL-рендер в'юпорта",
        ("*", "Final Render"): "Фінальний рендер",
        ("*", "Use scene render engine"): "Використовувати рушій рендера сцени",
        ("*", "Uses Output Path directory from Render Properties."): "Використовує каталог шляху виводу з властивостей рендера.",
        ("*", "Record"): "Запис",
        ("*", "Play"): "Відтворити",
        ("*", "Stop"): "Стоп",
        ("Operator", "Start Recording"): "Почати запис",
        ("Operator", "Stop Recording"): "Зупинити запис",
        ("Operator", "Play"): "Відтворити",
        ("Operator", "Stop"): "Стоп",
        ("Operator", "Record Frames"): "Записати кадри",
        ("Operator", "Stop Playing"): "Зупинити відтворення",
    },
}

# Global state
operation_history = []
redo_history = []
initial_hash = None
is_recording = False
is_playing = False
is_exporting_frames = False
current_step = 0
initial_mesh = None
last_hash = None
target_obj_name = None
interp_progress = 0.0

_step_cache = None  # vertex mapping cache for current playback step
_highlight_obj_name = (
    "__MeshRecorder_NewEdges"  # deprecated, no longer used in playback
)
_render_frame_idx = 0
_view_lock_state = {}
_video_render_handler = None  # deprecated (video export removed)
_prev_render_settings = None  # deprecated (video export removed)
_playback_start_idx = 0
_playback_end_idx = -1


def get_recorded_object():
    if not target_obj_name:
        return None
    obj = bpy.data.objects.get(target_obj_name)
    if obj and obj.type == "MESH":
        return obj
    return None


def get_mesh_hash(obj):
    if obj.mode == "EDIT":
        bm = bmesh.from_edit_mesh(obj.data)
        verts = tuple(
            (round(v.co.x, 4), round(v.co.y, 4), round(v.co.z, 4)) for v in bm.verts
        )
        edges = len(bm.edges)
    else:
        mesh = obj.data
        coords = [0.0] * (len(mesh.vertices) * 3)
        mesh.vertices.foreach_get("co", coords)
        verts = tuple(round(c, 4) for c in coords)
        edges = len(mesh.edges)
    return hash((verts, edges))


def save_mesh_state(obj):
    if obj.mode == "EDIT":
        bm = bmesh.from_edit_mesh(obj.data)
        verts = [v.co.copy() for v in bm.verts]
        edges = [(e.verts[0].index, e.verts[1].index) for e in bm.edges]
        faces = [tuple(v.index for v in f.verts) for f in bm.faces]
    else:
        verts = [v.co.copy() for v in obj.data.vertices]
        edges = [(e.vertices[0], e.vertices[1]) for e in obj.data.edges]
        faces = [tuple(f.vertices) for f in obj.data.polygons]
    return {"verts": verts, "edges": edges, "faces": faces}


def save_view_state(context):
    screen = context.screen or bpy.context.screen
    if not screen:
        return None
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            r3d = space.region_3d
            if r3d:
                return {
                    "view_perspective": r3d.view_perspective,
                    "view_location": r3d.view_location.copy(),
                    "view_rotation": r3d.view_rotation.copy(),
                    "view_distance": float(r3d.view_distance),
                }
    return None


def interpolate_view_state(state1, state2, t):
    if not state1 and not state2:
        return None
    if not state1:
        return {
            "view_perspective": state2.get("view_perspective", "PERSP"),
            "view_location": state2["view_location"].copy(),
            "view_rotation": state2["view_rotation"].copy(),
            "view_distance": float(state2.get("view_distance", 0.0)),
        }
    if not state2:
        return {
            "view_perspective": state1.get("view_perspective", "PERSP"),
            "view_location": state1["view_location"].copy(),
            "view_rotation": state1["view_rotation"].copy(),
            "view_distance": float(state1.get("view_distance", 0.0)),
        }

    loc = state1["view_location"].lerp(state2["view_location"], t)
    rot = state1["view_rotation"].slerp(state2["view_rotation"], t)
    dist1 = float(state1.get("view_distance", 0.0))
    dist2 = float(state2.get("view_distance", 0.0))
    dist = dist1 + (dist2 - dist1) * t
    perspective = state2.get(
        "view_perspective", state1.get("view_perspective", "PERSP")
    )
    return {
        "view_perspective": perspective,
        "view_location": loc,
        "view_rotation": rot,
        "view_distance": dist,
    }


def view_state_changed(state1, state2, loc_eps=1e-5, dist_eps=1e-5, ang_eps=1e-4):
    if state1 is None and state2 is None:
        return False
    if state1 is None or state2 is None:
        return True

    try:
        if (state1["view_location"] - state2["view_location"]).length > loc_eps:
            return True
        if (
            abs(
                float(state1.get("view_distance", 0.0))
                - float(state2.get("view_distance", 0.0))
            )
            > dist_eps
        ):
            return True
        q1 = state1["view_rotation"]
        q2 = state2["view_rotation"]
        if q1.rotation_difference(q2).angle > ang_eps:
            return True
        if state1.get("view_perspective") != state2.get("view_perspective"):
            return True
    except Exception:
        return True

    return False


def camera_state_changed(state1, state2, loc_eps=1e-5, ang_eps=1e-4):
    if state1 is None and state2 is None:
        return False
    if state1 is None or state2 is None:
        return True
    try:
        if (state1["location"] - state2["location"]).length > loc_eps:
            return True
        q1 = state1["rotation"]
        q2 = state2["rotation"]
        if q1.rotation_difference(q2).angle > ang_eps:
            return True
    except Exception:
        return True
    return False


def apply_view_state(context, state):
    if not state:
        return
    screen = context.screen or bpy.context.screen
    if not screen:
        return
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            r3d = space.region_3d
            if not r3d:
                continue
            r3d.view_perspective = state.get("view_perspective", r3d.view_perspective)
            r3d.view_location = state["view_location"]
            r3d.view_rotation = state["view_rotation"]
            r3d.view_distance = state.get("view_distance", r3d.view_distance)


# Backward-compat helpers for old recordings that used scene camera.
def save_camera_state(context):
    cam = context.scene.camera
    if not cam:
        return None
    if cam.rotation_mode == "QUATERNION":
        rot = cam.rotation_quaternion.copy()
    else:
        rot = cam.rotation_euler.to_quaternion()
    return {"location": cam.location.copy(), "rotation": rot}


def interpolate_camera_state(state1, state2, t):
    if not state1 and not state2:
        return None
    if not state1:
        return {
            "location": state2["location"].copy(),
            "rotation": state2["rotation"].copy(),
        }
    if not state2:
        return {
            "location": state1["location"].copy(),
            "rotation": state1["rotation"].copy(),
        }
    loc = state1["location"].lerp(state2["location"], t)
    rot = state1["rotation"].slerp(state2["rotation"], t)
    return {"location": loc, "rotation": rot}


def apply_camera_state(context, state):
    cam = context.scene.camera
    if not cam or not state:
        return
    cam.location = state["location"]
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = state["rotation"]


def lock_view_to_camera(context, lock):
    global _view_lock_state
    screen = context.screen or bpy.context.screen
    if not screen:
        return

    if lock:
        _view_lock_state.clear()
        for area in screen.areas:
            if area.type == "VIEW_3D":
                space = area.spaces.active
                r3d = space.region_3d
                if not r3d:
                    continue
                _view_lock_state[area.as_pointer()] = {
                    "view_perspective": r3d.view_perspective,
                    "view_location": r3d.view_location.copy(),
                    "view_rotation": r3d.view_rotation.copy(),
                    "view_distance": r3d.view_distance,
                }
        return

    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            r3d = space.region_3d
            if not r3d:
                continue
            state = _view_lock_state.get(area.as_pointer())
            if not state:
                continue
            r3d.view_perspective = state["view_perspective"]
            r3d.view_location = state["view_location"]
            r3d.view_rotation = state["view_rotation"]
            r3d.view_distance = state.get("view_distance", r3d.view_distance)
    _view_lock_state.clear()


def maybe_render_viewport_frame(context):
    global _render_frame_idx, is_exporting_frames
    if not is_exporting_frames:
        return

    settings = get_settings(context)
    scene = context.scene

    base_path = bpy.path.abspath(scene.render.filepath)
    out_dir = os.path.dirname(base_path) if base_path else bpy.path.abspath("//")
    os.makedirs(out_dir, exist_ok=True)

    def _ext_from_format(fmt):
        mapping = {
            "PNG": ".png",
            "JPEG": ".jpg",
            "JPEG2000": ".jp2",
            "OPEN_EXR": ".exr",
            "OPEN_EXR_MULTILAYER": ".exr",
            "TIFF": ".tif",
            "TARGA": ".tga",
            "TARGA_RAW": ".tga",
            "BMP": ".bmp",
            "WEBP": ".webp",
            "HDR": ".hdr",
            "DPX": ".dpx",
            "CINEON": ".cin",
            "IRIS": ".rgb",
        }
        return mapping.get(fmt, ".png")

    prev_path = scene.render.filepath
    prev_format = scene.render.image_settings.file_format
    prev_color_mode = scene.render.image_settings.color_mode

    target_format = prev_format
    movie_formats = {"FFMPEG", "AVI_JPEG", "AVI_RAW"}
    if target_format in movie_formats:
        target_format = "PNG"
        print(
            f"Movie format '{prev_format}' cannot be used for still frames; "
            "exporting PNG sequence instead."
        )

    ext = _ext_from_format(target_format)
    filepath = os.path.join(
        out_dir, f"{settings.render_prefix}_{_render_frame_idx:04d}{ext}"
    )

    scene.render.filepath = filepath
    scene.render.image_settings.file_format = target_format
    alpha_formats = {
        "PNG",
        "OPEN_EXR",
        "OPEN_EXR_MULTILAYER",
        "TIFF",
        "TARGA",
        "TARGA_RAW",
        "WEBP",
        "JPEG2000",
    }
    if (
        getattr(scene.render, "film_transparent", False)
        and target_format in alpha_formats
    ):
        scene.render.image_settings.color_mode = "RGBA"
    else:
        scene.render.image_settings.color_mode = prev_color_mode

    try:
        if settings.export_render_mode == "FINAL":
            bpy.ops.render.render(write_still=True, use_viewport=False)
        else:
            bpy.ops.render.opengl(write_still=True, view_context=True)
    except Exception as exc:
        print(f"Frame export failed: {exc}")
    finally:
        scene.render.filepath = prev_path
        scene.render.image_settings.file_format = prev_format
        scene.render.image_settings.color_mode = prev_color_mode

    _render_frame_idx += 1


def create_mesh_from_state(state, name="playback_mesh"):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    for co in state["verts"]:
        bm.verts.new(co)
    bm.verts.ensure_lookup_table()

    for e in state["edges"]:
        if e[0] < len(bm.verts) and e[1] < len(bm.verts):
            try:
                bm.edges.new((bm.verts[e[0]], bm.verts[e[1]]))
            except ValueError:
                pass

    for f in state["faces"]:
        try:
            bm.faces.new([bm.verts[i] for i in f])
        except ValueError:
            pass

    bm.to_mesh(mesh)
    bm.free()
    return mesh


def apply_state_to_object(obj, state, name_suffix="playback"):
    new_mesh = create_mesh_from_state(state, name=f"{obj.name}_{name_suffix}")
    old_mesh = obj.data
    obj.data = new_mesh
    if old_mesh and old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)


def get_or_create_highlight_object(target_obj):
    return None


def remove_highlight_object():
    return


def update_mesh_vertices(mesh, verts):
    if len(mesh.vertices) != len(verts):
        return False
    coords = array("f", (c for v in verts for c in v))
    mesh.vertices.foreach_set("co", coords)
    mesh.update()
    return True


def build_vertex_mapping(verts_src, verts_dst):
    """ """
    n_src = len(verts_src)
    n_dst = len(verts_dst)
    if n_src == 0:
        return [0] * n_dst

    kd = kdtree.KDTree(n_src)
    for i, v in enumerate(verts_src):
        kd.insert(v, i)
    kd.balance()

    mapping = [0] * n_dst
    for i, v in enumerate(verts_dst):
        _, idx, _ = kd.find(v)
        mapping[i] = idx
    return mapping


def compute_step_cache(source_state, target_state):
    verts1 = source_state["verts"]
    verts2 = target_state["verts"]
    n1 = len(verts1)
    n2 = len(verts2)

    # If topology is unchanged, prefer index-based interpolation.
    def _topo_signature(state):
        edges = state.get("edges") or []
        faces = state.get("faces") or []
        edges_sig = {tuple(sorted(e)) for e in edges}
        faces_sig = {tuple(sorted(f)) for f in faces}
        return edges_sig, faces_sig

    topo_same = False
    if n1 == n2:
        try:
            e1, f1 = _topo_signature(source_state)
            e2, f2 = _topo_signature(target_state)
            topo_same = (e1 == e2) and (f1 == f2)
        except Exception:
            topo_same = False
    if topo_same:
        return {
            "n1": n1,
            "n2": n2,
            "mode": "direct",
        }

    # If topology increases but all old verts are unchanged and new verts split old edges,
    # interpolate new verts from their parent edges to avoid nearest-neighbor flips.
    if n2 > n1:
        try:
            eps = 1e-6
            old_unchanged = all(
                (verts1[i] - verts2[i]).length <= eps for i in range(n1)
            )
        except Exception:
            old_unchanged = False

        if old_unchanged:
            source_edges = {tuple(sorted(e)) for e in (source_state.get("edges") or [])}
            target_edges = target_state.get("edges") or []
            old_new_edges = [(a, b) for a, b in target_edges if (a < n1) != (b < n1)]

            edge_splits = []
            ok = True
            for new_idx in range(n1, n2):
                olds = []
                for a, b in old_new_edges:
                    if a == new_idx and b < n1:
                        olds.append(b)
                    elif b == new_idx and a < n1:
                        olds.append(a)
                olds = sorted(set(olds))
                if len(olds) == 2 and tuple(sorted(olds)) in source_edges:
                    a_i, b_i = olds
                    va = verts1[a_i]
                    vb = verts1[b_i]
                    edge_vec = vb - va
                    denom = edge_vec.dot(edge_vec)
                    if denom > 0.0:
                        u = (verts2[new_idx] - va).dot(edge_vec) / denom
                    else:
                        u = 0.5
                    if u < 0.0:
                        u = 0.0
                    elif u > 1.0:
                        u = 1.0
                    edge_splits.append((a_i, b_i, float(u)))
                else:
                    ok = False
                    break

            if ok and len(edge_splits) == (n2 - n1):
                return {
                    "n1": n1,
                    "n2": n2,
                    "mode": "edge_split",
                    "edge_splits": edge_splits,
                }

    return {
        "n1": n1,
        "n2": n2,
        "mode": "mapped",
        "map_t2s": build_vertex_mapping(verts1, verts2),
        "map_s2t": build_vertex_mapping(verts2, verts1),
    }


def interpolate_states_cached(source_state, target_state, t, cache):
    verts1 = source_state["verts"]
    verts2 = target_state["verts"]
    n1 = cache["n1"]
    n2 = cache["n2"]

    if cache.get("mode") == "direct":
        new_verts = [verts1[i].lerp(verts2[i], t) for i in range(n1)]
        return new_verts, target_state

    if cache.get("mode") == "edge_split":
        edge_splits = cache.get("edge_splits") or []
        new_verts = [None] * n2
        for i in range(n1):
            new_verts[i] = verts1[i].lerp(verts2[i], t)
        for j, new_idx in enumerate(range(n1, n2)):
            try:
                a_i, b_i, u = edge_splits[j]
                va = verts1[a_i]
                vb = verts1[b_i]
                start_pos = va.lerp(vb, u)
                new_verts[new_idx] = start_pos.lerp(verts2[new_idx], t)
            except Exception:
                new_verts[new_idx] = verts2[new_idx].copy()
        return new_verts, target_state

    map_t2s = cache["map_t2s"]
    map_s2t = cache["map_s2t"]

    if n1 == 0:
        return [v.copy() for v in verts2], target_state
    if n2 == 0:
        return [v.copy() for v in verts1], source_state

    if n2 >= n1:
        new_verts = [verts1[map_t2s[i]].lerp(verts2[i], t) for i in range(n2)]
        topo = target_state
    else:
        if t <= 0.5:
            tt = t * 2.0
            new_verts = [verts1[i].lerp(verts2[map_s2t[i]], tt) for i in range(n1)]
            topo = source_state
        else:
            tt = (t - 0.5) * 2.0
            new_verts = [verts1[map_t2s[i]].lerp(verts2[i], tt) for i in range(n2)]
            topo = target_state

    return new_verts, topo


class MeshRecorderModal(bpy.types.Operator):
    bl_idname = "mesh.recorder_modal"
    bl_label = "Mesh Recorder Modal"
    bl_options = {"REGISTER"}

    _timer = None
    _stable_count = 0
    _pending_hash = None

    def modal(self, context, event):
        global operation_history, redo_history, initial_hash, last_hash, is_recording

        if not is_recording:
            self.cancel(context)
            return {"CANCELLED"}

        if event.type == "TIMER":
            obj = context.active_object
            if obj and obj.type == "MESH" and obj.name == target_obj_name:
                current_hash = get_mesh_hash(obj)
                if current_hash != last_hash:
                    if current_hash == self._pending_hash:
                        self._stable_count += 1
                        if self._stable_count >= 3:
                            base_hash = (
                                initial_hash if initial_hash is not None else last_hash
                            )
                            history_hashes = [base_hash] + [
                                s.get("hash") for s in operation_history
                            ]

                            # Undo: rollback to a previous step
                            if current_hash in history_hashes:
                                match_idx = history_hashes.index(current_hash)
                                keep_len = max(0, match_idx)
                                if keep_len < len(operation_history):
                                    removed = operation_history[keep_len:]
                                    redo_history[:] = removed + redo_history
                                    del operation_history[keep_len:]
                                    print(
                                        f"Undo detected, rollback to step {keep_len}, "
                                        f"redo available: {len(redo_history)}"
                                    )
                                last_hash = current_hash

                            else:
                                # Redo: move forward in redo stack
                                redo_hashes = [s.get("hash") for s in redo_history]
                                if current_hash in redo_hashes:
                                    redo_idx = redo_hashes.index(current_hash)
                                    restored = redo_history[: redo_idx + 1]
                                    operation_history.extend(restored)
                                    del redo_history[: redo_idx + 1]
                                    last_hash = current_hash
                                    print(
                                        f"Redo detected, step {len(operation_history)}, "
                                        f"redo remaining: {len(redo_history)}"
                                    )
                                else:
                                    # New operation: clear redo and append step                                     redo_history.clear()
                                    state = save_mesh_state(obj)
                                    state["view"] = save_view_state(context)
                                    state["camera"] = save_camera_state(context)
                                    state["hash"] = current_hash
                                    operation_history.append(state)
                                    last_hash = current_hash
                                    print(
                                        f"Recorded step {len(operation_history)}, "
                                        f"verts: {len(state['verts'])}, edges: {len(state['edges'])}"
                                    )

                            self._stable_count = 0
                            self._pending_hash = None
                    else:
                        self._pending_hash = current_hash
                        self._stable_count = 1

        return {"PASS_THROUGH"}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        self._stable_count = 0
        self._pending_hash = None
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None


def start_recording(context):
    global \
        is_recording, \
        initial_mesh, \
        initial_hash, \
        last_hash, \
        target_obj_name, \
        redo_history

    if is_playing:
        return

    obj = context.active_object
    if not obj or obj.type != "MESH":
        return

    operation_history.clear()
    redo_history.clear()
    target_obj_name = obj.name
    initial_mesh = save_mesh_state(obj)
    initial_mesh["view"] = save_view_state(context)
    initial_mesh["camera"] = save_camera_state(context)
    initial_hash = get_mesh_hash(obj)
    last_hash = initial_hash
    initial_mesh["hash"] = initial_hash
    is_recording = True

    bpy.ops.mesh.recorder_modal("INVOKE_DEFAULT")
    print(f"Recording started on {obj.name}")


def stop_recording():
    global is_recording, redo_history
    is_recording = False
    redo_history.clear()
    print(f"Recording stopped, total steps: {len(operation_history)}")


def get_settings(context):
    return context.scene.mesh_recorder_settings


def ensure_object_mode(context, obj):
    if obj.mode != "OBJECT":
        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="OBJECT")


def play_forward(context, export_frames=False):
    global \
        is_playing, \
        current_step, \
        interp_progress, \
        _step_cache, \
        _render_frame_idx, \
        _playback_start_idx, \
        _playback_end_idx, \
        is_exporting_frames

    if is_recording or is_playing or not operation_history:
        return

    obj = get_recorded_object()
    if not obj:
        print("No recorded target mesh")
        return

    ensure_object_mode(context, obj)
    apply_state_to_object(obj, initial_mesh, name_suffix="start")
    apply_view_state(context, initial_mesh.get("view"))
    apply_camera_state(context, initial_mesh.get("camera"))

    settings = get_settings(context)
    is_exporting_frames = bool(export_frames)

    start_idx = max(
        0, min(len(operation_history) - 1, settings.playback_start_step - 1)
    )
    end_idx = (
        settings.playback_end_step - 1
        if settings.playback_end_step > 0
        else len(operation_history) - 1
    )
    end_idx = max(start_idx, min(len(operation_history) - 1, end_idx))
    _playback_start_idx = start_idx
    _playback_end_idx = end_idx

    current_step = start_idx
    interp_progress = 0.0
    _step_cache = None
    _render_frame_idx = 0
    is_playing = True
    lock_view_to_camera(context, True)
    toggle_overlays(True)

    interval = settings.step_duration / max(1, settings.interp_steps)
    bpy.app.timers.register(lambda: play_step(context), first_interval=interval)
    print(f"Playing forward, total steps: {len(operation_history)}")


def play_step(context):
    global current_step, is_playing, interp_progress, _step_cache, _playback_end_idx

    if not is_playing:
        return None

    obj = get_recorded_object()
    if not obj:
        stop_playing()
        return None

    settings = get_settings(context)
    interp_steps = max(1, settings.interp_steps)
    interval = settings.step_duration / interp_steps

    if current_step > _playback_end_idx:
        stop_playing()
        return None

    target_state = operation_history[current_step]
    source_state = (
        initial_mesh if current_step == 0 else operation_history[current_step - 1]
    )

    cache_key = current_step
    if _step_cache is None or _step_cache.get("key") != cache_key:
        _step_cache = compute_step_cache(source_state, target_state)
        _step_cache["key"] = cache_key

    # Track elapsed time within this step.
    interp_progress += interval

    cam_changed = view_state_changed(
        source_state.get("view"), target_state.get("view")
    ) or camera_state_changed(source_state.get("camera"), target_state.get("camera"))

    cam_duration = 0.5 if cam_changed else 0.0
    mesh_duration = settings.step_duration
    total_duration = cam_duration + mesh_duration

    elapsed = interp_progress

    if cam_changed and elapsed < cam_duration:
        cam_t = elapsed / cam_duration if cam_duration > 0.0 else 1.0
        mesh_t = 0.0
    else:
        cam_t = 1.0 if cam_changed else min(elapsed / mesh_duration, 1.0)
        mesh_elapsed = elapsed - cam_duration if cam_changed else elapsed
        mesh_t = min(mesh_elapsed / max(mesh_duration, 1e-6), 1.0)

    if elapsed >= total_duration:
        apply_view_state(context, target_state.get("view"))
        apply_camera_state(context, target_state.get("camera"))
        apply_state_to_object(obj, target_state)
        maybe_render_viewport_frame(context)

        current_step += 1
        interp_progress = 0.0
        _step_cache = None
        return interval

    # Camera / view interpolation phase.
    apply_view_state(
        context,
        interpolate_view_state(
            source_state.get("view"), target_state.get("view"), cam_t
        ),
    )
    apply_camera_state(
        context,
        interpolate_camera_state(
            source_state.get("camera"), target_state.get("camera"), cam_t
        ),
    )

    # Mesh interpolation only after camera phase completes.
    if not (cam_changed and elapsed < cam_duration):
        new_verts, topo_state = interpolate_states_cached(
            source_state, target_state, mesh_t, _step_cache
        )
        if not update_mesh_vertices(obj.data, new_verts):
            apply_state_to_object(
                obj,
                {
                    "verts": new_verts,
                    "edges": topo_state["edges"],
                    "faces": topo_state["faces"],
                },
            )

    maybe_render_viewport_frame(context)

    return interval


def highlight_new_edges(obj, prev_state, curr_state, mapping_prev_to_curr=None):
    """ """
    return
    prev_edges_raw = prev_state["edges"]
    curr_edges_raw = curr_state["edges"]

    # Map prev_state vertex indices into curr_state space
    if mapping_prev_to_curr is None:
        mapping_prev_to_curr = build_vertex_mapping(
            curr_state["verts"], prev_state["verts"]
        )

    prev_edges_mapped = set()
    for a, b in prev_edges_raw:
        if a < len(mapping_prev_to_curr) and b < len(mapping_prev_to_curr):
            a2 = mapping_prev_to_curr[a]
            b2 = mapping_prev_to_curr[b]
            if a2 != b2:
                prev_edges_mapped.add((min(a2, b2), max(a2, b2)))

    curr_edges = set((min(e), max(e)) for e in curr_edges_raw)
    new_edges = curr_edges - prev_edges_mapped

    highlight_obj = get_or_create_highlight_object(obj)
    highlight_state = {
        "verts": curr_state["verts"],
        "edges": list(new_edges),
        "faces": [],
    }
    apply_state_to_object(highlight_obj, highlight_state, name_suffix="highlight")
    highlight_obj.hide_viewport = False


def stop_playing():
    global is_playing, _step_cache, interp_progress, is_exporting_frames
    is_playing = False
    _step_cache = None
    interp_progress = 0.0
    is_exporting_frames = False
    lock_view_to_camera(bpy.context, False)
    toggle_overlays(False)
    print("Playing stopped")


def toggle_overlays(hide):
    screen = bpy.context.screen
    if not screen:
        return
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.overlay.show_cursor = not hide
            space.overlay.show_floor = not hide
            space.overlay.show_edge_crease = hide


class MeshRecorderSettings(bpy.types.PropertyGroup):
    step_duration: bpy.props.FloatProperty(
        name="Step Duration",
        description="Seconds between steps",
        default=0.5,
        min=0.1,
        max=5.0,
    )
    interp_steps: bpy.props.IntProperty(
        name="Interpolation Steps",
        description="Interpolation frames per step",
        default=10,
        min=1,
        max=60,
    )
    playback_start_step: bpy.props.IntProperty(
        name="Start Step",
        description="First recorded step to replay (1-based)",
        default=1,
        min=1,
    )
    playback_end_step: bpy.props.IntProperty(
        name="End Step",
        description="Last recorded step to replay (1-based, 0 = to end)",
        default=0,
        min=0,
    )
    render_prefix: bpy.props.StringProperty(
        name="File Prefix",
        description="Frame file prefix",
        default="frame",
    )
    export_render_mode: bpy.props.EnumProperty(
        name="Export Render Mode",
        description="How to render frames when recording",
        items=[
            ("VIEWPORT", "Viewport", "Use OpenGL viewport render"),
            ("FINAL", "Final Render", "Use scene render engine"),
        ],
        default="VIEWPORT",
    )


class MeshRecorderPanel(bpy.types.Panel):
    bl_label = "Shaping Recorder"
    bl_idname = "MESH_PT_recorder"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Shaping Recorder"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.mesh_recorder_settings

        layout.label(text=iface_("Steps: {n}").format(n=len(operation_history)))
        row = layout.row()
        if not is_recording:
            row.operator("mesh.start_recording", text=iface_("Start Recording"))
        else:
            row.operator("mesh.stop_recording", text=iface_("Stop Recording"))

        layout.separator()
        layout.prop(settings, "step_duration")
        layout.prop(settings, "interp_steps")

        layout.separator()
        layout.label(
            text=iface_("Replay Range (1..{n})").format(n=len(operation_history))
        )
        row = layout.row(align=True)
        row.prop(settings, "playback_start_step")
        row.prop(settings, "playback_end_step")

        layout.separator()
        layout.label(text=iface_("Frame Export (Sequence)"))
        layout.prop(settings, "render_prefix")
        layout.prop(settings, "export_render_mode")
        layout.label(text=iface_("Uses Output Path directory from Render Properties."))

        layout.separator()
        row = layout.row(align=True)
        row.operator("mesh.record_frames", text=iface_("Record"))
        row.operator("mesh.play_forward", text=iface_("Play"))
        layout.operator("mesh.stop_playing", text=iface_("Stop"))


class StartRecordingOperator(bpy.types.Operator):
    bl_idname = "mesh.start_recording"
    bl_label = "Start Recording"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and not is_recording and not is_playing

    def execute(self, context):
        start_recording(context)
        return {"FINISHED"}


class StopRecordingOperator(bpy.types.Operator):
    bl_idname = "mesh.stop_recording"
    bl_label = "Stop Recording"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_recording

    def execute(self, context):
        stop_recording()
        return {"FINISHED"}


class PlayForwardOperator(bpy.types.Operator):
    bl_idname = "mesh.play_forward"
    bl_label = "Play"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (not is_recording) and (not is_playing) and bool(operation_history)

    def execute(self, context):
        play_forward(context, export_frames=False)
        return {"FINISHED"}


class RecordFramesOperator(bpy.types.Operator):
    bl_idname = "mesh.record_frames"
    bl_label = "Record Frames"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (not is_recording) and (not is_playing) and bool(operation_history)

    def execute(self, context):
        play_forward(context, export_frames=True)
        return {"FINISHED"}


class StopPlayingOperator(bpy.types.Operator):
    bl_idname = "mesh.stop_playing"
    bl_label = "Stop Playing"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_playing

    def execute(self, context):
        stop_playing()
        return {"FINISHED"}


classes = (
    MeshRecorderSettings,
    MeshRecorderModal,
    MeshRecorderPanel,
    StartRecordingOperator,
    StopRecordingOperator,
    PlayForwardOperator,
    RecordFramesOperator,
    StopPlayingOperator,
)


def register():
    bpy.app.translations.register(__name__, translations)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mesh_recorder_settings = bpy.props.PointerProperty(
        type=MeshRecorderSettings
    )


def unregister():
    stop_playing()
    if hasattr(bpy.types.Scene, "mesh_recorder_settings"):
        del bpy.types.Scene.mesh_recorder_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.app.translations.unregister(__name__)
