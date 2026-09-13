const { createApp, ref, reactive, computed, onMounted, nextTick } = Vue;

const I18N = {
  zh: {
    subtitle: "極簡流暢的 MKV 批次封裝工作站",
    tab_videos: "影片",
    tab_attachments: "附件",
    tab_mux_setting: "封裝",
    tab_settings: "設定",
    videos: "影片清單",
    attachments: "字型與附件",
    mux_setting: "封裝設定",
    settings: "偏好與預設",
    video_source: "影片來源目錄",
    browse_folder: "瀏覽目錄",
    refresh: "重新掃描",
    extensions: "副檔名篩選",
    default_fps: "預設 FPS / 時長覆蓋",
    modify_old_tracks: "修改軌道",
    modify_old_tracks_bulk: "修改軌道",
    modify_old_tracks_desc: "若有多部影片，此處設定會套用到所有來源影片中的對應軌道號碼。",
    files_found: "已找到檔案",
    total_size: "總容量",
    no_videos_selected: "尚未選擇影片，請點選上方「瀏覽目錄」選擇資料夾",
    attachments_source: "字型與附件檔案目錄",
    discard_old_attachments: "捨棄原影片舊附件",
    allow_duplicate_attachments: "允許重複附件",
    attachments_to_add: "即將新增的附件清單",
    clear_all: "清空",
    no_attachments_found: "目錄中無附件檔案",
    destination_and_output: "輸出目的地與常規選項",
    output_directory: "輸出目的地目錄",
    overwrite_source_files: "覆蓋來源檔案 (完成後自動替換)",
    use_mkvpropedit: "極速原地修改 (使用 mkvpropedit)",
    add_crc32: "計算並在檔名追加 CRC32",
    remove_old_crc: "若檔名已有舊 CRC 則先移除",
    abort_on_errors: "遭遇錯誤時立即終止隊列",
    track_filtering_options: "進階軌道過濾",
    only_keep_those_audios: "只保留指定音軌 (白名單)",
    only_keep_those_subtitles: "只保留指定字幕軌 (白名單)",
    refresh_tracks: "重新分析影片軌道",
    make_this_audio_default: "指定預設音軌 (其餘自動降級)",
    make_this_subtitle_default: "指定預設字幕軌 (其餘自動降級)",
    select_track: "選擇軌道/語言/名稱",
    presets_management: "預設集管理",
    save_current_as_preset: "將目前全部設定儲存為新預設集",
    save: "儲存",
    existing_presets: "已有預設集",
    delete: "刪除",
    default_folders: "預設工作目錄",
    default_video_dir: "預設影片目錄",
    default_output_dir: "預設輸出目錄",
    save_settings: "儲存設定",
    ready: "就緒",
    videos_selected: "部影片已選",
    click_start_to_mux: "點擊右側按鈕開始批次封裝",
    muxing: "封裝處理中",
    paused: "已暫停",
    start_muxing: "開始封裝",
    stop: "終止",
    pause: "暫停",
    resume: "繼續",
    clear_queue: "清空隊列",
    select_server_folder: "選取伺服器上的目錄",
    quick_jump: "快速切換",
    go_up: "上一層",
    selected: "目前選取",
    cancel: "取消",
    select_this_folder: "選擇此目錄",
    batch_queue_and_logs: "批次任務隊列",
    overall_progress: "總體進度",
    jobs: "任務清單",
    apply: "套用設定",
    queue_is_empty: "任務隊列目前為空，可點選上方「加入隊列」或「開始封裝」",
    add_to_queue: "加入隊列",
    select_all: "全選",
    deselect_all: "取消全選",
    queue_ready: "隊列就緒",
    pending_jobs: "個待處理任務",
    click_start_to_process: "點擊「開始封裝」執行隊列任務",
    click_add_to_queue: "可於「封裝設定」點選「加入隊列」",
    same_dir_muxed_notice: "輸出目錄與來源相同。未開啟覆蓋時，將自動輸出為 [檔名]_muxed.mkv 以確保原始檔案安全。",
    overwrite_warning_notice: "已啟用覆蓋來源檔案：封裝完成後將直接取代原始檔案（操作不可逆）。",
    theme_toggle: "切換外觀風格 (深色 / 淺色)",
    appearance_and_language: "介面外觀與顯示語言",
    theme_setting: "主題風格",
    light_mode: "淺色模式",
    dark_mode: "深色模式",
    language_setting: "介面語言",
    lang_zh: "繁體中文",
    lang_en: "English",
    active_preset: "目前使用中預設集",
    filters_active: "項已啟用",
    collapse: "收起",
    expand: "展開",
    general_options: "常規封裝選項",
    overwrite_badge: "覆蓋來源",
    abort_badge: "出錯停止",
    default: "預設",
    no_videos_selected_short: "尚未選擇影片",
    stopped: "隊列已終止",
    same_dir_protect_title: "同目錄輸出保護確認",
    same_dir_protect_desc: "輸出目錄與來源相同，且未開啟覆蓋",
    same_dir_protect_action: "為避免覆蓋原始檔案並確保安全，點選同意後系統將自動在輸出檔名加上「_muxed」後綴（例如：檔名_muxed.mkv）。",
    same_dir_protect_skip: "若您點擊取消，系統將略過本次處理作業，不變更任何檔案。",
    agree_add_muxed_and_start: "同意加入 _muxed 並開始封裝",
    agree_add_muxed_and_queue: "同意加入 _muxed 並排入隊列",
    skip_operation: "取消 (略過本次處理)",
    video_scan_options: "副檔名篩選與預設 FPS",
    video_tracks: "視訊軌道",
    audio_tracks: "音訊軌道",
    subtitle_tracks: "字幕軌道",
    track: "軌道",
    track_name: "軌道名稱",
    language: "語言",
    track_default: "預設",
    track_forced: "強制",
    old_setting: "[保留原設定]",
    channels: "聲道",
    info: "資訊",
    track_ids: "軌道 ID",
    track_languages: "語言",
    track_names: "軌道名稱",
    language_label: "語言",
    name_label: "名稱",
    default_label: "預設",
    forced_label: "強制",
    none: "(無)",
    yes: "是",
    no: "否",
    remove_job: "移除任務",
    theme_and_locale: "主題與語言偏好",
    custom_configs: "自訂設定檔",
    path_settings: "路徑偏好",
    preset_name_placeholder: "預設集名稱...",
    default_preset: "預設設定檔",
    source_path_label: "來源路徑",
    safe_output_label: "安全輸出",
    original_filename_label: "原檔名",
    status_idle: "閒置",
    status_running: "處理中",
    status_paused: "已暫停",
    status_stopped: "已終止",
    status_completed: "已完成",
    status_failed: "失敗",
    status_pending: "排隊中",
    status_cancelled: "已取消",
    expand_all_names: "展開全部檔名",
    collapse_all_names: "收起全部檔名",
    click_to_expand: "點擊查看完整檔名",
    click_to_collapse: "點擊收起檔名",
  },
  en: {
    subtitle: "Streamlined MKV Batch Muxing Suite",
    tab_videos: "Videos",
    tab_attachments: "Attachments",
    tab_mux_setting: "Mux Setting",
    tab_settings: "Settings",
    videos: "Videos",
    attachments: "Fonts & Attachments",
    mux_setting: "Mux Setting",
    settings: "Settings",
    video_source: "Video Source Directory",
    browse_folder: "Browse Folder",
    refresh: "Refresh",
    extensions: "Extensions",
    default_fps: "Default Duration / FPS",
    modify_old_tracks: "Modify Tracks",
    modify_old_tracks_bulk: "Modify Tracks",
    modify_old_tracks_desc: "These bulk modifications apply to matching track numbers across all source videos.",
    files_found: "Files Found",
    total_size: "Total Size",
    no_videos_selected: "No videos selected. Click 'Browse Folder' above.",
    attachments_source: "Fonts & Attachments Directory",
    discard_old_attachments: "Discard old attachments",
    allow_duplicate_attachments: "Allow duplicate attachments",
    attachments_to_add: "Attachments to Add",
    clear_all: "Clear All",
    no_attachments_found: "No attachments found in folder",
    destination_and_output: "Destination & Basic Options",
    output_directory: "Output Directory",
    overwrite_source_files: "Overwrite source files",
    use_mkvpropedit: "Fast In-place Editing (mkvpropedit)",
    add_crc32: "Add CRC32 to filename [A1B2C3D4]",
    remove_old_crc: "Remove old CRC from filename",
    abort_on_errors: "Abort queue on error",
    track_filtering_options: "Track Filtering Options",
    only_keep_those_audios: "Only keep those audios",
    only_keep_those_subtitles: "Only keep those subtitles",
    refresh_tracks: "Refresh Tracks Analysis",
    make_this_audio_default: "Make this audio default",
    make_this_subtitle_default: "Make this subtitle default",
    select_track: "Select Track / Language / Name",
    presets_management: "Presets Management",
    save_current_as_preset: "Save Current as Preset",
    save: "Save",
    existing_presets: "Presets",
    delete: "Delete",
    default_folders: "Default Folders",
    default_video_dir: "Default Video Dir",
    default_output_dir: "Default Output Dir",
    save_settings: "Save Settings",
    ready: "Ready",
    videos_selected: "video(s) selected",
    click_start_to_mux: "Click Start Muxing to begin",
    muxing: "Muxing in progress",
    paused: "Paused",
    start_muxing: "Start Muxing",
    stop: "Stop",
    pause: "Pause",
    resume: "Resume",
    clear_queue: "Clear Queue",
    select_server_folder: "Select Server Folder",
    quick_jump: "Quick Roots",
    go_up: "Go Up",
    selected: "Selected",
    cancel: "Cancel",
    select_this_folder: "Select Folder",
    batch_queue_and_logs: "Batch Jobs Queue",
    overall_progress: "Overall Progress",
    jobs: "Jobs",
    apply: "Apply Settings",
    queue_is_empty: "Queue is currently empty. Click 'Add to Queue' or 'Start Muxing'.",
    add_to_queue: "Add to Queue",
    select_all: "Select All",
    deselect_all: "Deselect All",
    queue_ready: "Queue Ready",
    pending_jobs: "pending job(s)",
    click_start_to_process: "Click Start Muxing to process queue",
    click_add_to_queue: "Click 'Add to Queue' in Mux Setting",
    same_dir_muxed_notice: "Output directory matches source. With overwrite disabled, output will be safely saved as [name]_muxed.mkv.",
    overwrite_warning_notice: "Overwrite source files is enabled: Original files will be replaced upon completion (irreversible).",
    theme_toggle: "Toggle Appearance (Dark / Light)",
    appearance_and_language: "Appearance & Language",
    theme_setting: "Interface Theme",
    light_mode: "Light Mode",
    dark_mode: "Dark Mode",
    language_setting: "Interface Language",
    lang_zh: "繁體中文",
    lang_en: "English",
    active_preset: "Active Preset",
    filters_active: "active",
    collapse: "Collapse",
    expand: "Expand",
    general_options: "General Options",
    overwrite_badge: "Overwrite",
    abort_badge: "Abort on Error",
    default: "Default",
    no_videos_selected_short: "No videos selected",
    stopped: "Queue stopped",
    same_dir_protect_title: "Same Directory Protection",
    same_dir_protect_desc: "Output directory is same as source and overwrite is off",
    same_dir_protect_action: "To protect your original files from being overwritten, agreeing will append a '_muxed' suffix to output filenames (e.g. filename_muxed.mkv).",
    same_dir_protect_skip: "If you cancel, this operation will be skipped without changes.",
    agree_add_muxed_and_start: "Agree with _muxed & Start",
    agree_add_muxed_and_queue: "Agree with _muxed & Add to Queue",
    skip_operation: "Cancel (Skip Operation)",
    video_scan_options: "Extension Filter & Default FPS",
    video_tracks: "Video Tracks",
    audio_tracks: "Audio Tracks",
    subtitle_tracks: "Subtitle Tracks",
    track: "Track",
    track_name: "Track Name",
    language: "Language",
    track_default: "Default",
    track_forced: "Forced",
    old_setting: "[Keep Old]",
    channels: "Channels",
    info: "Info",
    track_ids: "Track IDs",
    track_languages: "Languages",
    track_names: "Track Names",
    language_label: "Language",
    name_label: "Name",
    default_label: "Default",
    forced_label: "Forced",
    none: "(none)",
    yes: "Yes",
    no: "No",
    remove_job: "Remove Job",
    theme_and_locale: "Theme & Locale",
    custom_configs: "Custom configs",
    path_settings: "Path settings",
    preset_name_placeholder: "Preset name...",
    default_preset: "Default Preset",
    source_path_label: "Source Path",
    safe_output_label: "Safe Output",
    original_filename_label: "Original Filename",
    status_idle: "Idle",
    status_running: "Running",
    status_paused: "Paused",
    status_stopped: "Stopped",
    status_completed: "Completed",
    status_failed: "Failed",
    status_pending: "Pending",
    status_cancelled: "Cancelled",
    expand_all_names: "Expand All",
    collapse_all_names: "Collapse All",
    click_to_expand: "Click to expand full filename",
    click_to_collapse: "Click to collapse filename",
  }
};

const app = createApp({
  setup() {
    const lang = ref(localStorage.getItem("lang") || "zh");
    const t = (key) => I18N[lang.value]?.[key] || key;
    const setLang = (val) => {
      lang.value = val;
      localStorage.setItem("lang", val);
    };
    const toggleLang = () => {
      setLang(lang.value === "zh" ? "en" : "zh");
    };

    // Theme Management (Light / Dark)
    const getInitialTheme = () => {
      const stored = localStorage.getItem("theme");
      if (stored) return stored;
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    };
    const theme = ref(getInitialTheme());
    const isDark = computed(() => theme.value === "dark");

    const applyTheme = (val) => {
      localStorage.setItem("theme", val);
      if (val === "dark") {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    };

    const setTheme = (val) => {
      theme.value = val;
      applyTheme(val);
    };

    const toggleTheme = () => {
      setTheme(theme.value === "dark" ? "light" : "dark");
    };

    const activeTab = ref("videos");
    const tabs = computed(() => [
      { id: "videos", name: "tab_videos", icon: "film" },
      { id: "attachments", name: "tab_attachments", icon: "paperclip" },
      { id: "mux_setting", name: "tab_mux_setting", icon: "sliders" },
      { id: "settings", name: "tab_settings", icon: "settings" },
    ]);

    // Data lists
    const allLanguages = ref([]);
    const presets = ref([]);
    const currentPresetId = ref("default");
    const newPresetName = ref("");
    const appSettings = ref({
      default_video_dir: "/storage",
      default_output_dir: "/storage",
    });

    // Videos Tab State
    const videoDir = ref("/storage");
    const allVideoExts = ["mkv", "mp4", "avi", "ts", "m2ts", "mov", "webm"];
    const selectedVideoExts = ref(["mkv", "mp4"]);
    const videoFps = ref("Default");
    const fpsOptions = ["Default", "23.976p", "24p", "25p", "29.97p", "30p", "50p", "59.94p", "60p"];
    const videosList = ref([]);
    const totalVideosSize = computed(() => videosList.value.reduce((sum, v) => sum + (v.size || 0), 0));
    const selectedVideos = computed(() => videosList.value.filter(v => v.selected));
    const selectedVideosCount = computed(() => selectedVideos.value.length);
    const isAllVideosSelected = computed(() => videosList.value.length > 0 && selectedVideos.value.length === videosList.value.length);
    const toggleSelectAllVideos = (e) => {
      const val = e.target.checked;
      videosList.value.forEach(v => v.selected = val);
    };
    const selectAllVideos = (val) => {
      videosList.value.forEach(v => v.selected = val);
    };

    // Toast Notification State
    const toast = ref({ message: "", type: "info" });
    let toastTimer = null;
    const showToast = (message, type = "info") => {
      toast.value = { message, type };
      if (toastTimer) clearTimeout(toastTimer);
      toastTimer = setTimeout(() => {
        toast.value = { message: "", type: "info" };
      }, 3500);
    };

    // Attachments Tab State
    const attachmentDir = ref("/storage");
    const attachmentFiles = ref([]);
    const attachmentsDiscardOld = ref(false);
    const attachmentsAllowDuplicates = ref(false);

    // Mux Setting Tab State
    const outputDir = ref("/storage");
    const overwriteSource = ref(false);
    const useMkvpropedit = ref(false);
    const addCrc = ref(false);
    const removeOldCrc = ref(false);
    const abortOnError = ref(false);

    const onOverwriteChange = () => {
      if (overwriteSource.value) {
        const confirmed = confirm(
          lang.value === 'zh'
            ? '[警告]：開啟「覆蓋來源檔案」後，封裝成功時將會直接替換並覆寫原始影片檔案，此操作無法復原！\n\n確定要開啟覆蓋嗎？'
            : '[Warning]: Enabling "Overwrite source files" will replace the original video files upon completion. This cannot be undone!\n\nAre you sure you want to enable overwrite?'
        );
        if (!confirmed) {
          overwriteSource.value = false;
        }
      }
    };

    const onlyKeepAudiosEnabled = ref(false);
    const onlyKeepAudiosIds = ref([]);
    const onlyKeepAudiosLangs = ref([]);
    const onlyKeepAudiosNames = ref([]);

    const onlyKeepSubtitlesEnabled = ref(false);
    const onlyKeepSubtitlesIds = ref([]);
    const onlyKeepSubtitlesLangs = ref([]);
    const onlyKeepSubtitlesNames = ref([]);

    const makeAudioDefaultEnabled = ref(false);
    const makeAudioDefaultTarget = ref("");

    const makeSubtitleDefaultEnabled = ref(false);
    const makeSubtitleDefaultTarget = ref("");

    // Collapsible general options state & active count
    const isGeneralOptionsOpen = ref(false);
    const activeGeneralOptionsCount = computed(() => {
      let count = 0;
      if (overwriteSource.value) count++;
      if (useMkvpropedit.value) count++;
      if (addCrc.value) count++;
      if (removeOldCrc.value) count++;
      if (abortOnError.value) count++;
      return count;
    });

    // Collapsible video filter & FPS options
    const isVideoFilterOpen = ref(false);

    // Collapsible track filtering panel state & active count
    const isTrackFilteringOpen = ref(false);
    const activeTrackFiltersCount = computed(() => {
      let count = 0;
      if (onlyKeepAudiosEnabled.value) count++;
      if (onlyKeepSubtitlesEnabled.value) count++;
      if (makeAudioDefaultEnabled.value) count++;
      if (makeSubtitleDefaultEnabled.value) count++;
      return count;
    });

    // Bulk old tracks analysis
    const batchAnalysis = ref({
      audios: { ids: [], languages: [], names: [] },
      subtitles: { ids: [], languages: [], names: [] },
      bulk_tracks: { videos: [], audios: [], subtitles: [] }
    });
    const oldTrackSettings = reactive({});

    // Modals
    const showFilePickerModal = ref(false);
    const showInfoModal = ref(false);
    const showModifyTracksModal = ref(false);
    const inspectData = ref(null);

    // Server-Side File Picker State
    const pickerTarget = ref("");
    const pickerData = ref({
      current_path: "/storage",
      parent_path: null,
      quick_roots: [],
      directories: [],
      files: []
    });

    // Queue & Terminal Logs State
    const queueState = ref({
      status: "idle",
      current_job_index: -1,
      total_jobs: 0,
      jobs: [],
    });
    const terminalLogs = ref([]);
    const logContainer = ref(null);

    const completedJobsCount = computed(() => {
      if (!queueState.value.jobs) return 0;
      return queueState.value.jobs.filter(j => j.status === 'completed').length;
    });

    const pendingJobsCount = computed(() => {
      if (!queueState.value.jobs) return 0;
      return queueState.value.jobs.filter(j => j.status === 'pending').length;
    });

    const overallProgressPercent = computed(() => {
      if (!queueState.value.jobs || queueState.value.jobs.length === 0) return 0;
      const totalPct = queueState.value.jobs.reduce((sum, j) => sum + (j.progress || 0), 0);
      return Math.round(totalPct / queueState.value.jobs.length);
    });

    const currentRunningJobName = computed(() => {
      if (queueState.value.jobs && queueState.value.current_job_index >= 0) {
        const j = queueState.value.jobs[queueState.value.current_job_index];
        return j ? j.source_name : "";
      }
      return "";
    });

    // Helpers
    const formatBytes = (bytes) => {
      if (!bytes || bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const toggleExt = (type, ext) => {
      if (type === 'video') {
        const idx = selectedVideoExts.value.indexOf(ext);
        if (idx >= 0) selectedVideoExts.value.splice(idx, 1);
        else selectedVideoExts.value.push(ext);
      }
    };

    const toggleItem = (arr, item) => {
      const idx = arr.indexOf(item);
      if (idx >= 0) arr.splice(idx, 1);
      else arr.push(item);
    };

    const jumpToMuxSetting = () => {
      activeTab.value = 'mux_setting';
      nextTick(() => {
        const el = document.getElementById('job-queue-section');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      });
    };

    // File Picker Functions
    const openFilePicker = async (target) => {
      pickerTarget.value = target;
      let initialPath = "/storage";
      if (target === "video_dir") initialPath = videoDir.value;
      else if (target === "attach_dir") initialPath = attachmentDir.value;
      else if (target === "output_dir") initialPath = outputDir.value;
      else if (target === "default_video_dir") initialPath = appSettings.value.default_video_dir;
      else if (target === "default_output_dir") initialPath = appSettings.value.default_output_dir;

      await fetchBrowse(initialPath);
      showFilePickerModal.value = true;
    };

    const fetchBrowse = async (path) => {
      try {
        const query = path ? `?path=${encodeURIComponent(path)}` : "";
        const res = await fetch(`/api/files/browse${query}`);
        if (res.ok) {
          pickerData.value = await res.json();
        }
      } catch (e) {
        console.error("Failed to browse:", e);
      }
    };

    const confirmPickerSelection = () => {
      const selected = pickerData.value.current_path;
      if (pickerTarget.value === "video_dir") {
        videoDir.value = selected;
        scanVideos();
      } else if (pickerTarget.value === "attach_dir") {
        attachmentDir.value = selected;
        scanAttachments();
      } else if (pickerTarget.value === "output_dir") {
        outputDir.value = selected;
      } else if (pickerTarget.value === "default_video_dir") {
        appSettings.value.default_video_dir = selected;
      } else if (pickerTarget.value === "default_output_dir") {
        appSettings.value.default_output_dir = selected;
      }
      showFilePickerModal.value = false;
    };

    // Scanning APIs
    const scanVideos = async () => {
      try {
        const res = await fetch("/api/files/list_files", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ directory: videoDir.value, extensions: selectedVideoExts.value })
        });
        if (res.ok) {
          const data = await res.json();
          videosList.value = (data.files || []).map(f => ({ ...f, selected: true, expanded: false }));
          if (!outputDir.value || outputDir.value === "/storage") {
            outputDir.value = videoDir.value;
          }
          analyzeTracks();
        }
      } catch (e) {
        console.error("Scan videos failed:", e);
      }
    };

    const isAllVideosExpanded = computed(() => {
      return videosList.value.length > 0 && videosList.value.every(v => v.expanded);
    });

    const toggleExpandAllVideos = () => {
      const target = !isAllVideosExpanded.value;
      videosList.value.forEach(v => { v.expanded = target; });
    };

    const toggleExpandVideo = (v) => {
      v.expanded = !v.expanded;
    };

    const scanAttachments = async () => {
      try {
        const res = await fetch("/api/files/list_files", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            directory: attachmentDir.value,
            extensions: ["ttf", "otf", "ttc", "woff", "woff2", "jpg", "jpeg", "png", "xml", "txt"]
          })
        });
        if (res.ok) {
          const data = await res.json();
          attachmentFiles.value = (data.files || []).map(f => ({ ...f, expanded: false }));
        }
      } catch (e) {
        console.error("Scan attachments failed:", e);
      }
    };

    const isAllAttachmentsExpanded = computed(() => {
      return attachmentFiles.value.length > 0 && attachmentFiles.value.every(a => a.expanded);
    });

    const toggleExpandAllAttachments = () => {
      const target = !isAllAttachmentsExpanded.value;
      attachmentFiles.value.forEach(a => { a.expanded = target; });
    };

    const toggleExpandAttachment = (att) => {
      att.expanded = !att.expanded;
    };

    // Queue jobs expansion tracking using Set of job IDs (preserves expansion across SSE/polling updates)
    const expandedJobIds = ref(new Set());
    const isJobExpanded = (id) => expandedJobIds.value.has(id);
    const toggleExpandJob = (id) => {
      if (expandedJobIds.value.has(id)) {
        expandedJobIds.value.delete(id);
      } else {
        expandedJobIds.value.add(id);
      }
    };
    const isAllJobsExpanded = computed(() => {
      const jobs = queueState.value.jobs || [];
      return jobs.length > 0 && jobs.every(j => expandedJobIds.value.has(j.id));
    });
    const toggleExpandAllJobs = () => {
      const jobs = queueState.value.jobs || [];
      if (isAllJobsExpanded.value) {
        expandedJobIds.value.clear();
      } else {
        jobs.forEach(j => expandedJobIds.value.add(j.id));
      }
    };

    // Inspect video
    const inspectVideo = async (path) => {
      try {
        const res = await fetch("/api/videos/inspect", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ file_path: path })
        });
        if (res.ok) {
          inspectData.value = await res.json();
          showInfoModal.value = true;
        }
      } catch (e) {
        alert((lang.value === "zh" ? "分析影片失敗: " : "Failed to inspect video: ") + e.message);
      }
    };

    // Analyze tracks across batch
    const analyzeTracks = async () => {
      if (videosList.value.length === 0) return;
      try {
        const paths = videosList.value.map(v => v.path);
        const res = await fetch("/api/videos/analyze_tracks", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ file_paths: paths })
        });
        if (res.ok) {
          batchAnalysis.value = await res.json();
          const allTrks = [
            ...batchAnalysis.value.bulk_tracks.videos,
            ...batchAnalysis.value.bulk_tracks.audios,
            ...batchAnalysis.value.bulk_tracks.subtitles,
          ];
          for (const t of allTrks) {
            if (!oldTrackSettings[t.id]) {
              oldTrackSettings[t.id] = {
                is_enabled: t.is_enabled,
                track_name: t.track_name,
                language: t.language,
                is_default: t.is_default,
                is_forced: t.is_forced,
              };
            }
          }
        }
      } catch (e) {
        console.error("Failed to analyze tracks:", e);
      }
    };

    const openModifyOldTracksModal = async () => {
      await analyzeTracks();
      showModifyTracksModal.value = true;
    };

    const showMuxedConfirmModal = ref(false);
    const pendingMuxAction = ref(null);

    const isSameDirWithoutOverwrite = () => {
      const vDir = (videoDir.value || "").trim().replace(/[/\\]+$/, "");
      const oDir = (outputDir.value || videoDir.value || "").trim().replace(/[/\\]+$/, "");
      return !!vDir && vDir === oDir && !overwriteSource.value;
    };

    const cancelMuxedConfirm = () => {
      showMuxedConfirmModal.value = false;
      pendingMuxAction.value = null;
      showToast(lang.value === 'zh' ? '已取消本次操作，略過處理' : 'Operation skipped', 'info');
    };

    const confirmMuxedProceed = async () => {
      showMuxedConfirmModal.value = false;
      const action = pendingMuxAction.value;
      pendingMuxAction.value = null;

      if (action === 'start') {
        await startMuxingBatch(true);
      } else if (action === 'queue') {
        await addCurrentToQueue(true);
      }
    };

    // Add selected videos and current configuration to Queue
    const addCurrentToQueue = async (bypassConfirm = false) => {
      const selected = videosList.value.filter(v => v.selected);
      if (selected.length === 0) {
        alert(lang.value === 'zh' ? '請先在「影片清單」勾選至少一部影片！' : 'Please select at least one video in the Videos tab!');
        return false;
      }

      if (!bypassConfirm && isSameDirWithoutOverwrite()) {
        pendingMuxAction.value = 'queue';
        showMuxedConfirmModal.value = true;
        return false;
      }

      const attachments = attachmentFiles.value.map(a => ({ file_path: a.path }));

      const jobsConfigs = selected.map(v => ({
        source_video: v.path,
        output_dir: outputDir.value || videoDir.value,
        video_fps: videoFps.value,
        old_tracks_modifications: oldTrackSettings,
        subtitles: [],
        audios: [],
        chapter_file: null,
        chapter_discard_old: false,
        attachments: attachments,
        attachments_discard_old: attachmentsDiscardOld.value,
        attachments_allow_duplicates: attachmentsAllowDuplicates.value,
        overwrite_source: overwriteSource.value,
        use_mkvpropedit: useMkvpropedit.value,
        add_crc: addCrc.value,
        remove_old_crc: removeOldCrc.value,
        only_keep_audios_enabled: onlyKeepAudiosEnabled.value,
        only_keep_audios_ids: onlyKeepAudiosIds.value,
        only_keep_audios_langs: onlyKeepAudiosLangs.value,
        only_keep_audios_names: onlyKeepAudiosNames.value,
        only_keep_subtitles_enabled: onlyKeepSubtitlesEnabled.value,
        only_keep_subtitles_ids: onlyKeepSubtitlesIds.value,
        only_keep_subtitles_langs: onlyKeepSubtitlesLangs.value,
        only_keep_subtitles_names: onlyKeepSubtitlesNames.value,
        make_audio_default_enabled: makeAudioDefaultEnabled.value,
        make_audio_default_target: makeAudioDefaultTarget.value,
        make_subtitle_default_enabled: makeSubtitleDefaultEnabled.value,
        make_subtitle_default_target: makeSubtitleDefaultTarget.value,
      }));

      try {
        const res = await fetch("/api/mux/queue/add", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ jobs: jobsConfigs })
        });
        if (res.ok) {
          queueState.value = await res.json();
          showToast(
            lang.value === 'zh'
              ? `已成功加入 ${jobsConfigs.length} 個任務到隊列！`
              : `Added ${jobsConfigs.length} job(s) to queue!`
          );
          jumpToMuxSetting();
          return true;
        } else {
          const err = await res.json();
          alert((lang.value === "zh" ? "加入任務失敗: " : "Failed to add jobs: ") + (err.detail || (lang.value === "zh" ? "未知錯誤" : "Unknown error")));
          return false;
        }
      } catch (e) {
        alert((lang.value === "zh" ? "網路錯誤: " : "Network error: ") + e.message);
        return false;
      }
    };

    // Remove single job from queue
    const removeJob = async (jobIdx) => {
      try {
        const res = await fetch(`/api/mux/queue/${jobIdx}`, { method: "DELETE" });
        if (res.ok) {
          queueState.value = await res.json();
        }
      } catch (e) {
        console.error("Failed to remove job:", e);
      }
    };

    // Start Batch Muxing
    const startMuxingBatch = async (bypassConfirm = false) => {
      const pendingCount = (queueState.value.jobs || []).filter(j => j.status === 'pending').length;
      if (pendingCount === 0) {
        if (selectedVideosCount.value > 0) {
          if (!bypassConfirm && isSameDirWithoutOverwrite()) {
            pendingMuxAction.value = 'start';
            showMuxedConfirmModal.value = true;
            return;
          }
          const added = await addCurrentToQueue(true);
          if (!added) return;
        } else {
          alert(lang.value === 'zh' ? '隊列中沒有待處理任務，請先勾選影片並加入隊列！' : 'No pending jobs in queue. Please select videos and add them to queue first!');
          return;
        }
      }

      try {
        const res = await fetch("/api/mux/start", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ abort_on_error: abortOnError.value })
        });
        if (res.ok) {
          queueState.value = await res.json();
          jumpToMuxSetting();
          showToast(
            lang.value === 'zh'
              ? '已開始批次封裝處理！'
              : 'Batch muxing started!'
          );
        } else {
          const err = await res.json();
          alert((lang.value === "zh" ? "啟動封裝失敗: " : "Error starting muxing: ") + (err.detail || (lang.value === "zh" ? "未知錯誤" : "Unknown error")));
        }
      } catch (e) {
        alert((lang.value === "zh" ? "網路錯誤: " : "Network error: ") + e.message);
      }
    };

    const stopMuxingBatch = async () => {
      const res = await fetch("/api/mux/stop", { method: "POST" });
      if (res.ok) {
        queueState.value = await res.json();
      }
    };

    const pauseQueue = async () => {
      const res = await fetch("/api/mux/pause", { method: "POST" });
      if (res.ok) {
        queueState.value = await res.json();
      }
    };

    const resumeQueue = async () => {
      const res = await fetch("/api/mux/resume", { method: "POST" });
      if (res.ok) {
        queueState.value = await res.json();
      }
    };

    // Fully working Clear Queue!
    const clearQueue = async () => {
      try {
        const res = await fetch("/api/mux/clear", { method: "POST" });
        if (res.ok) {
          const state = await res.json();
          queueState.value = state;
          terminalLogs.value = [];
        }
      } catch (e) {
        console.error("Failed to clear queue:", e);
      }
    };

    // Presets Management
    const loadPresets = async () => {
      try {
        const res = await fetch("/api/presets");
        if (res.ok) {
          presets.value = await res.json();
        }
      } catch (e) {
        console.error("Failed to load presets:", e);
      }
    };

    const onPresetChange = () => {
      const p = presets.value.find(x => x.id === currentPresetId.value);
      if (p && p.settings) {
        const s = p.settings;
        videoFps.value = s.video_fps || "Default";
        attachmentsDiscardOld.value = s.attachments_discard_old || false;
        attachmentsAllowDuplicates.value = s.attachments_allow_duplicates || false;
        overwriteSource.value = s.overwrite_source || false;
        useMkvpropedit.value = s.use_mkvpropedit || false;
        addCrc.value = s.add_crc || false;
        removeOldCrc.value = s.remove_old_crc || false;
        abortOnError.value = s.abort_on_error || false;
        onlyKeepAudiosEnabled.value = s.only_keep_audios_enabled || false;
        onlyKeepAudiosIds.value = s.only_keep_audios_ids || [];
        onlyKeepAudiosLangs.value = s.only_keep_audios_langs || [];
        onlyKeepAudiosNames.value = s.only_keep_audios_names || [];
        onlyKeepSubtitlesEnabled.value = s.only_keep_subtitles_enabled || false;
        onlyKeepSubtitlesIds.value = s.only_keep_subtitles_ids || [];
        onlyKeepSubtitlesLangs.value = s.only_keep_subtitles_langs || [];
        onlyKeepSubtitlesNames.value = s.only_keep_subtitles_names || [];
        makeAudioDefaultEnabled.value = s.make_audio_default_enabled || false;
        makeAudioDefaultTarget.value = s.make_audio_default_target || "";
        makeSubtitleDefaultEnabled.value = s.make_subtitle_default_enabled || false;
        makeSubtitleDefaultTarget.value = s.make_subtitle_default_target || "";
      }
    };

    const saveNewPreset = async () => {
      if (!newPresetName.value.trim()) return;
      const settings = {
        video_fps: videoFps.value,
        attachments_discard_old: attachmentsDiscardOld.value,
        attachments_allow_duplicates: attachmentsAllowDuplicates.value,
        overwrite_source: overwriteSource.value,
        use_mkvpropedit: useMkvpropedit.value,
        add_crc: addCrc.value,
        remove_old_crc: removeOldCrc.value,
        abort_on_error: abortOnError.value,
        only_keep_audios_enabled: onlyKeepAudiosEnabled.value,
        only_keep_audios_ids: onlyKeepAudiosIds.value,
        only_keep_audios_langs: onlyKeepAudiosLangs.value,
        only_keep_audios_names: onlyKeepAudiosNames.value,
        only_keep_subtitles_enabled: onlyKeepSubtitlesEnabled.value,
        only_keep_subtitles_ids: onlyKeepSubtitlesIds.value,
        only_keep_subtitles_langs: onlyKeepSubtitlesLangs.value,
        only_keep_subtitles_names: onlyKeepSubtitlesNames.value,
        make_audio_default_enabled: makeAudioDefaultEnabled.value,
        make_audio_default_target: makeAudioDefaultTarget.value,
        make_subtitle_default_enabled: makeSubtitleDefaultEnabled.value,
        make_subtitle_default_target: makeSubtitleDefaultTarget.value,
      };

      try {
        const res = await fetch("/api/presets", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: newPresetName.value.trim(), settings })
        });
        if (res.ok) {
          const created = await res.json();
          await loadPresets();
          currentPresetId.value = created.id;
          newPresetName.value = "";
          showToast(
            lang.value === "zh" ? "預設集儲存成功！" : "Preset saved successfully!",
            "success"
          );
        }
      } catch (e) {
        showToast(
          (lang.value === "zh" ? "儲存預設集失敗: " : "Failed to save preset: ") + e.message,
          "error"
        );
      }
    };

    const deleteCurrentPreset = async () => {
      if (currentPresetId.value === "default") return;
      if (!confirm(lang.value === "zh" ? "確定要刪除此預設集嗎？" : "Are you sure you want to delete this preset?")) return;
      try {
        const res = await fetch(`/api/presets/${currentPresetId.value}`, { method: "DELETE" });
        if (res.ok) {
          currentPresetId.value = "default";
          await loadPresets();
          onPresetChange();
          showToast(
            lang.value === "zh" ? "預設集已刪除" : "Preset deleted",
            "info"
          );
        }
      } catch (e) {
        showToast(
          (lang.value === "zh" ? "刪除預設集失敗: " : "Failed to delete preset: ") + e.message,
          "error"
        );
      }
    };

    // App Settings
    const loadAppSettings = async () => {
      try {
        const res = await fetch("/api/presets/settings/app");
        if (res.ok) {
          const s = await res.json();
          appSettings.value = s;
          if (s.default_video_dir) videoDir.value = s.default_video_dir;
          if (s.default_output_dir) outputDir.value = s.default_output_dir;
        }
      } catch (e) {
        console.error("Failed to load app settings:", e);
      }
    };

    const saveAppSettings = async () => {
      try {
        const res = await fetch("/api/presets/settings/app", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(appSettings.value)
        });
        if (res.ok) {
          showToast(
            lang.value === "zh" ? "偏好路徑設定已儲存！" : "Settings saved successfully!",
            "success"
          );
        }
      } catch (e) {
        showToast(
          (lang.value === "zh" ? "儲存設定失敗: " : "Failed to save settings: ") + e.message,
          "error"
        );
      }
    };

    // WebSocket real-time updates
    const connectWebSocket = () => {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${protocol}//${window.location.host}/api/ws`;
      const socket = new WebSocket(wsUrl);

      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (
            msg.type === "initial_state" ||
            msg.type === "queue_started" ||
            msg.type === "job_finished" ||
            msg.type === "queue_finished" ||
            msg.type === "queue_stopped" ||
            msg.type === "queue_cleared" ||
            msg.type === "queue_updated" ||
            msg.type === "queue_paused" ||
            msg.type === "queue_resumed"
          ) {
            if (msg.data) queueState.value = msg.data;

            if (msg.type === "job_finished" && msg.data && msg.data.jobs && msg.data.jobs[msg.job_index]) {
              const j = msg.data.jobs[msg.job_index];
              if (j.status === "completed") {
                showToast(
                  lang.value === "zh"
                    ? `任務完成：${j.source_name}`
                    : `Job completed: ${j.source_name}`,
                  "success"
                );
              } else if (j.status === "failed") {
                showToast(
                  lang.value === "zh"
                    ? `任務失敗：${j.source_name}${j.error ? ' - ' + j.error : ''}`
                    : `Job failed: ${j.source_name}${j.error ? ' - ' + j.error : ''}`,
                  "error"
                );
              }
            } else if (msg.type === "queue_finished") {
              showToast(
                lang.value === "zh"
                  ? "所有封裝任務皆已完成！"
                  : "All muxing jobs have completed!",
                "success"
              );
            } else if (msg.type === "queue_stopped") {
              showToast(
                lang.value === "zh"
                  ? "封裝隊列已停止"
                  : "Muxing queue stopped",
                "info"
              );
            }
          } else if (msg.type === "job_progress") {
            if (queueState.value.jobs && queueState.value.jobs[msg.job_index]) {
              queueState.value.jobs[msg.job_index].progress = msg.progress;
            }
          }
        } catch (e) {
          console.error("WS error:", e);
        }
      };

      socket.onclose = () => {
        setTimeout(connectWebSocket, 3000);
      };
    };

    onMounted(async () => {
      try {
        const res = await fetch("/api/presets/languages");
        if (res.ok) allLanguages.value = await res.json();
      } catch (e) {}

      await loadAppSettings();
      await loadPresets();
      connectWebSocket();

      // Listen for OS theme preference changes if not pinned in localStorage
      window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
        if (!localStorage.getItem("theme")) {
          theme.value = e.matches ? "dark" : "light";
          applyTheme(theme.value);
        }
      });
    });

    return {
      theme,
      isDark,
      toggleTheme,
      setTheme,
      lang,
      t,
      toggleLang,
      setLang,
      activeTab,
      tabs,
      allLanguages,
      presets,
      currentPresetId,
      newPresetName,
      appSettings,
      videoDir,
      allVideoExts,
      selectedVideoExts,
      videoFps,
      fpsOptions,
      videosList,
      totalVideosSize,
      selectedVideos,
      selectedVideosCount,
      isAllVideosSelected,
      toggleSelectAllVideos,
      selectAllVideos,
      toast,
      showToast,
      pendingJobsCount,
      addCurrentToQueue,
      removeJob,
      attachmentDir,
      attachmentFiles,
      attachmentsDiscardOld,
      attachmentsAllowDuplicates,
      outputDir,
      overwriteSource,
      useMkvpropedit,
      addCrc,
      removeOldCrc,
      abortOnError,
      onlyKeepAudiosEnabled,
      onlyKeepAudiosIds,
      onlyKeepAudiosLangs,
      onlyKeepAudiosNames,
      onlyKeepSubtitlesEnabled,
      onlyKeepSubtitlesIds,
      onlyKeepSubtitlesLangs,
      onlyKeepSubtitlesNames,
      makeAudioDefaultEnabled,
      makeAudioDefaultTarget,
      makeSubtitleDefaultEnabled,
      makeSubtitleDefaultTarget,
      isVideoFilterOpen,
      isTrackFilteringOpen,
      activeTrackFiltersCount,
      isGeneralOptionsOpen,
      activeGeneralOptionsCount,
      batchAnalysis,
      oldTrackSettings,
      showFilePickerModal,
      showInfoModal,
      showModifyTracksModal,
      inspectData,
      pickerTarget,
      pickerData,
      queueState,
      terminalLogs,
      logContainer,
      completedJobsCount,
      overallProgressPercent,
      currentRunningJobName,
      formatBytes,
      toggleExt,
      toggleItem,
      jumpToMuxSetting,
      openFilePicker,
      fetchBrowse,
      confirmPickerSelection,
      scanVideos,
      scanAttachments,
      inspectVideo,
      analyzeTracks,
      openModifyOldTracksModal,
      startMuxingBatch,
      stopMuxingBatch,
      pauseQueue,
      resumeQueue,
      clearQueue,
      onOverwriteChange,
      showMuxedConfirmModal,
      pendingMuxAction,
      cancelMuxedConfirm,
      confirmMuxedProceed,
      onPresetChange,
      saveNewPreset,
      deleteCurrentPreset,
      saveAppSettings,
      isAllVideosExpanded,
      toggleExpandAllVideos,
      toggleExpandVideo,
      isAllAttachmentsExpanded,
      toggleExpandAllAttachments,
      toggleExpandAttachment,
      expandedJobIds,
      isJobExpanded,
      toggleExpandJob,
      isAllJobsExpanded,
      toggleExpandAllJobs,
    };
  }
});

// Register Reactive Lucide Icon Component
app.component('icon', {
  props: {
    name: { type: String, required: true },
    class: { type: String, default: 'w-4 h-4' }
  },
  setup(props) {
    const toPascal = (str) => {
      if (!str) return '';
      return str.split('-').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join('');
    };

    const getSvg = () => {
      if (!window.lucide || !window.lucide.icons) return '';
      const pascal = toPascal(props.name);
      const iconDef = window.lucide.icons[pascal] || window.lucide.icons[props.name];
      if (!iconDef) return '';
      let children = '';
      for (const [tag, attrs] of iconDef) {
        const attrStr = Object.entries(attrs).map(([k, v]) => `${k}="${v}"`).join(' ');
        children += `<${tag} ${attrStr}></${tag}>`;
      }
      return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="${props.class}">${children}</svg>`;
    };

    return { getSvg };
  },
  template: `<span class="inline-flex items-center justify-center shrink-0 leading-none" v-html="getSvg()"></span>`
});

app.mount("#app");
