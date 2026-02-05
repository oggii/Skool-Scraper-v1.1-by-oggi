class Dashboard {
    constructor() {
        this.currentPage = 'dashboard';
        this.mapData = null;
        this.settings = { target_url: '', output_dir: '' };
        this.init();
    }

    async init() {
        this.setupNavigation();
        this.setupEventListeners();
        await this.loadSettings();
        this.loadStats();
        this.loadMapData();
    }

    async loadSettings() {
        try {
            const resp = await fetch('/api/settings');
            this.settings = await resp.json();
            document.getElementById('setting-url').value = this.settings.target_url || '';
            document.getElementById('setting-output').value = this.settings.output_dir || '';
            this.updateLogic();
        } catch (e) { console.error('Settings load fail', e); }
    }

    updateLogic() {
        const scrapeBtn = document.getElementById('btn-scrape');
        const dlBtn = document.getElementById('btn-start-download');
        const mapHint = document.getElementById('mapper-hint');
        const dlHint = document.getElementById('download-hint');
        const globalStatus = document.getElementById('global-status');

        if (!this.settings.target_url) {
            scrapeBtn.disabled = true;
            mapHint.textContent = '⚠️ Set Target URL in Settings first.';
            globalStatus.textContent = 'Setup Required';
        } else {
            scrapeBtn.disabled = false;
            mapHint.textContent = '✅ URL Ready';
            globalStatus.textContent = 'Ready';
        }

        if (this.mapData && this.mapData.courses && this.mapData.courses.length > 0) {
            dlBtn.disabled = false;
            dlHint.textContent = `✅ Map loaded (${this.mapData.courses.length} courses). Files sink: ${this.settings.output_dir || 'downloads'}`;
        } else {
            dlBtn.disabled = true;
            dlHint.textContent = '⚠️ You must Map the course first.';
        }
    }

    setupNavigation() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const page = item.dataset.page;
                document.querySelectorAll('.nav-item').forEach(n => n.classList.toggle('active', n === item));
                document.querySelectorAll('.page').forEach(p => p.classList.toggle('active', p.id === `page-${page}`));
                this.currentPage = page;
                if (page === 'courses' && this.mapData) this.renderCourseTree();
                if (page === 'dashboard') this.loadStats();
            });
        });
    }

    setupEventListeners() {
        document.getElementById('btn-refresh')?.addEventListener('click', () => { this.loadStats(); this.loadMapData(); });
        document.getElementById('btn-scrape')?.addEventListener('click', () => this.runStreamingTask('scrape'));
        document.getElementById('btn-start-download')?.addEventListener('click', () => this.runStreamingTask('download'));
        document.getElementById('btn-view-map')?.addEventListener('click', () => {
            const coursesTab = document.querySelector('.nav-item[data-page="courses"]');
            if (coursesTab) coursesTab.click();
        });
        document.getElementById('btn-save-settings')?.addEventListener('click', () => this.saveSettings());
        document.getElementById('btn-pick-folder')?.addEventListener('click', () => this.pickFolder());
        document.getElementById('course-search')?.addEventListener('input', (e) => this.filterCourses(e.target.value));
    }

    async runStreamingTask(type) {
        const btnId = type === 'scrape' ? 'btn-scrape' : 'btn-start-download';
        const logId = type === 'scrape' ? 'scrape-output' : 'download-output';
        const cardId = type === 'scrape' ? 'scrape-output-card' : null;
        const btn = document.getElementById(btnId);
        const pre = document.getElementById(logId);
        const card = cardId ? document.getElementById(cardId) : null;

        btn.disabled = true;
        if (card) card.style.display = 'block';
        pre.style.display = 'block';
        pre.textContent = `🚀 Initializing ${type === 'scrape' ? 'Mapper' : 'Downloader'}...\n`;

        try {
            const response = await fetch(`/api/${type}`, { method: 'POST' });
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                pre.textContent += decoder.decode(value, { stream: true });
                pre.scrollTop = pre.scrollHeight;
            }

            pre.textContent += `\n✅ ${type.toUpperCase()} COMPLETE!`;
            this.loadStats();
            this.loadMapData();
        } catch (e) { pre.textContent += `\n❌ ERROR: ${e}`; }
        btn.disabled = false;
    }

    async pickFolder() {
        try {
            const resp = await fetch('/api/pick-folder');
            const data = await resp.json();
            if (data.folder) {
                document.getElementById('setting-output').value = data.folder;
                this.settings.output_dir = data.folder;
            }
        } catch (e) { alert('Folder picker error'); }
    }

    async saveSettings() {
        const status = document.getElementById('settings-status');
        const url = document.getElementById('setting-url').value;
        const out = document.getElementById('setting-output').value;
        status.textContent = 'Saving...';
        try {
            await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_url: url, output_dir: out })
            });
            this.settings.target_url = url;
            this.settings.output_dir = out;
            status.textContent = '✅ Saved!';
            status.className = 'status-msg success';
            this.updateLogic();
            setTimeout(() => { status.textContent = ''; }, 3000);
        } catch (e) { status.textContent = '❌ Error'; }
    }

    async loadStats() {
        const btn = document.getElementById('btn-refresh');
        if (btn) btn.classList.add('refreshing');

        try {
            const resp = await fetch('/api/stats');
            const s = await resp.json();
            document.getElementById('stat-courses').textContent = s.courses || 0;
            document.getElementById('stat-modules').textContent = s.modules || 0;
            document.getElementById('stat-videos').textContent = s.videos || 0;
            document.getElementById('stat-attachments').textContent = s.attachments || 0;
            this.updateLogic();
        } catch (e) {
            console.error('Stats refresh failed', e);
        } finally {
            if (btn) setTimeout(() => btn.classList.remove('refreshing'), 500);
        }
    }

    async loadMapData() {
        try {
            const resp = await fetch('/api/map');
            if (resp.ok) {
                this.mapData = await resp.json();
                this.updateLogic();
            }
        } catch (e) { }
    }

    renderCourseTree() {
        const container = document.getElementById('course-tree');
        if (!this.mapData || !this.mapData.courses) {
            container.innerHTML = '<p class="loading-text">No data. Map the course first.</p>';
            return;
        }
        let html = '';
        this.mapData.courses.forEach(c => {
            const h = c.details?.hierarchy || [];
            html += `
                <div class="tree-course">
                    <div class="tree-course-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block'">
                        <span class="tree-course-title">📂 ${this.escapeHtml(c.title)}</span>
                    </div>
                    <div class="tree-course-children" style="display:none; padding-left:20px;">
                        ${this.renderNodes(h)}
                    </div>
                </div>`;
        });
        container.innerHTML = html;
    }

    renderNodes(nodes) {
        let html = '';
        nodes.forEach(n => {
            if (n.unitType === 'set') {
                html += `<div><strong>📁 ${n.title}</strong><div style="padding-left:15px">${this.renderNodes(n.children || [])}</div></div>`;
            } else {
                html += `<div>📄 ${n.title}</div>`;
            }
        });
        return html;
    }

    filterCourses(q) {
        q = q.toLowerCase();
        document.querySelectorAll('.tree-course').forEach(c => {
            c.style.display = c.textContent.toLowerCase().includes(q) ? 'block' : 'none';
        });
    }

    escapeHtml(t) {
        const d = document.createElement('div');
        d.textContent = t;
        return d.innerHTML;
    }
}
document.addEventListener('DOMContentLoaded', () => { window.dashboard = new Dashboard(); });
