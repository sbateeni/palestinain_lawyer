import { core } from './core.js';

export class CaseManager {
    constructor() {
        this.currentCaseId = null;
        this.currentStage = 1;
        this.isAnalyzing = false;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeFilters();
            this.initializeSortButtons();
        });
    }

    initializeFilters() {
        const filterInputs = document.querySelectorAll('.case-filter');
        filterInputs.forEach(input => {
            input.addEventListener('change', () => this.filterCases());
        });
    }

    initializeSortButtons() {
        const sortButtons = document.querySelectorAll('.sort-btn');
        sortButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const sortBy = e.target.dataset.sort;
                this.sortCases(sortBy);
            });
        });
    }

    async loadCase(caseId) {
        try {
            const response = await fetch(`/case/${caseId}`);
            const data = await response.json();
            
            if (data.error) throw new Error(data.error);
            
            this.currentCaseId = caseId;
            this.displayCaseDetails(data);
            
            return data;
        } catch (error) {
            core.showNotification(error.message, 'error');
        }
    }

    displayCaseDetails(caseData) {
        const detailsContainer = document.getElementById('caseDetails');
        if (!detailsContainer) return;

        detailsContainer.innerHTML = `
            <div class="case-header">
                <h2>${caseData.title}</h2>
                <div class="meta-info">
                    <span class="date">
                        <i class="fas fa-calendar"></i>
                        ${core.formatDate(caseData.date)}
                    </span>
                    <span class="model">
                        <i class="fas fa-robot"></i>
                        ${caseData.model_name}
                    </span>
                </div>
            </div>
            <div class="case-content">
                ${this.formatStages(caseData.stages)}
            </div>
        `;
    }

    formatStages(stages) {
        if (!stages) return '';
        
        return Object.entries(stages).map(([stage, data]) => `
            <div class="stage-item">
                <div class="stage-header">
                    <h3>المرحلة ${stage}</h3>
                    <span class="timestamp">${core.formatDate(data.timestamp)}</span>
                </div>
                <div class="stage-content">
                    ${core.formatContent(data.content)}
                </div>
            </div>
        `).join('');
    }

    filterCases() {
        const searchTerm = document.getElementById('searchInput')?.value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter')?.value;
        const dateFilter = document.getElementById('dateFilter')?.value;

        document.querySelectorAll('.case-card').forEach(card => {
            const title = card.querySelector('.case-title')?.textContent.toLowerCase();
            const status = card.dataset.status;
            const date = new Date(card.dataset.date);

            let show = true;

            if (searchTerm) {
                show = show && title.includes(searchTerm);
            }

            if (statusFilter) {
                show = show && status === statusFilter;
            }

            if (dateFilter) {
                const today = new Date();
                const diffDays = Math.floor((today - date) / (1000 * 60 * 60 * 24));
                
                switch(dateFilter) {
                    case 'today':
                        show = show && diffDays === 0;
                        break;
                    case 'week':
                        show = show && diffDays <= 7;
                        break;
                    case 'month':
                        show = show && diffDays <= 30;
                        break;
                }
            }

            card.style.display = show ? 'block' : 'none';
        });
    }

    sortCases(sortBy) {
        const casesContainer = document.querySelector('.cases-grid');
        if (!casesContainer) return;

        const cards = Array.from(casesContainer.children);
        
        cards.sort((a, b) => {
            switch(sortBy) {
                case 'date':
                    return new Date(b.dataset.date) - new Date(a.dataset.date);
                case 'title':
                    return a.querySelector('.case-title').textContent
                        .localeCompare(b.querySelector('.case-title').textContent);
                default:
                    return 0;
            }
        });

        casesContainer.innerHTML = '';
        cards.forEach(card => casesContainer.appendChild(card));
    }
}

export const caseManager = new CaseManager(); 