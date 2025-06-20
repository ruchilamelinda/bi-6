HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Global Styles */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            :root {
                --primary-color: #01875f;
                --secondary-color: #00b894;
                --accent-color: #4285f4;
                --warning-color: #ffa500;
                --danger-color: #ea4335;
                --success-color: #34c759;
                --light-bg: #f8f9fa;
                --white: #ffffff;
                --gray-100: #f1f3f4;
                --gray-200: #e8eaed;
                --gray-300: #dadce0;
                --gray-400: #9aa0a6;
                --gray-500: #5f6368;
                --gray-700: #3c4043;
                --gray-900: #202124;
                --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
                --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
                --shadow-lg: 0 8px 25px rgba(0,0,0,0.15);
                --shadow-xl: 0 12px 35px rgba(0,0,0,0.2);
                --radius-sm: 8px;
                --radius-md: 12px;
                --radius-lg: 16px;
                --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            body {
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                background: var(--light-bg);
                min-height: 100vh;
                line-height: 1.6;
                color: var(--gray-700);
                overflow-x: hidden;
            }

            .dashboard-container {
                min-height: 100vh;
                background: linear-gradient(135deg, var(--light-bg) 0%, #e8f4f8 100%);
                position: relative;
            }

            .dashboard-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 300px;
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--accent-color) 100%);
                z-index: -1;
                clip-path: polygon(0 0, 100% 0, 100% 70%, 0 100%);
            }

            /* Header Styles with Enhanced Design */
            .main-header {
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--accent-color) 100%);
                color: white;
                padding: 3rem 2rem;
                position: relative;
                overflow: hidden;
            }

            .main-header::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: shimmer 8s ease-in-out infinite;
            }

            @keyframes shimmer {
                0%, 100% { transform: rotate(0deg) translate(-50%, -50%); }
                50% { transform: rotate(180deg) translate(-50%, -50%); }
            }

            .header-content {
                position: relative;
                z-index: 2;
                max-width: 1200px;
                margin: 0 auto;
            }

            .header-title {
                font-size: clamp(2rem, 4vw, 3rem);
                font-weight: 800;
                margin-bottom: 0.5rem;
                text-shadow: 0 2px 10px rgba(0,0,0,0.2);
                letter-spacing: -0.02em;
            }

            .header-title i {
                animation: pulse 2s ease-in-out infinite;
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }

            .header-subtitle {
                font-size: 1.25rem;
                opacity: 0.9;
                font-weight: 400;
            }

            /* Enhanced Metrics Cards */
            .metrics-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-top: 2.5rem;
                position: relative;
                z-index: 2;
            }

            .metric-card {
                background: rgba(255,255,255,0.95);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: var(--radius-lg);
                padding: 2rem;
                display: flex;
                align-items: center;
                gap: 1.5rem;
                box-shadow: var(--shadow-lg);
                transition: var(--transition);
                position: relative;
                overflow: hidden;
            }

            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            }

            .metric-card:hover {
                transform: translateY(-5px) scale(1.02);
                box-shadow: var(--shadow-xl);
                background: rgba(255,255,255,1);
            }

            .metric-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                border-radius: 50%;
                color: white;
                transition: var(--transition);
            }

            .metric-card:hover .metric-icon {
                transform: rotate(5deg) scale(1.1);
            }

            .metric-content {
                flex: 1;
            }

            .metric-number {
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
                color: var(--gray-900);
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .metric-label {
                font-size: 1rem;
                color: var(--gray-500);
                font-weight: 500;
            }

            /* Dashboard Body Layout */
            .dashboard-body {
                display: flex;
                min-height: calc(100vh - 200px);
                max-width: 1600px;
                margin: 0 auto;
                gap: 2rem;
                padding: 2rem;
            }

            /* Enhanced Sidebar */
            .sidebar {
                width: 380px;
                background: var(--white);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
                padding: 2rem;
                height: fit-content;
                position: sticky;
                top: 2rem;
                transition: var(--transition);
            }

            .sidebar:hover {
                box-shadow: var(--shadow-lg);
            }

            /* Filter Section */
            .filters-section {
                margin-bottom: 2rem;
            }

            .section-title {
                color: var(--gray-900);
                margin-bottom: 1.5rem;
                font-size: 1.4rem;
                font-weight: 700;
                position: relative;
                padding-left: 1rem;
            }

            .section-title::before {
                content: '';
                position: absolute;
                left: 0;
                top: 50%;
                transform: translateY(-50%);
                width: 4px;
                height: 20px;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                border-radius: 2px;
            }

            .filters-grid {
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
            }

            .filter-item {
                background: var(--gray-100);
                padding: 1.5rem;
                border-radius: var(--radius-md);
                transition: var(--transition);
            }

            .filter-item:hover {
                background: var(--gray-200);
                transform: translateX(5px);
            }

            .filter-label {
                display: block;
                margin-bottom: 0.75rem;
                font-weight: 600;
                color: var(--gray-700);
            }

            /* Custom Dropdown Styles */
            .custom-dropdown .Select-control {
                border: 2px solid var(--gray-300);
                border-radius: var(--radius-sm);
                min-height: 45px;
                transition: var(--transition);
            }

            .custom-dropdown .Select-control:hover {
                border-color: var(--primary-color);
            }

            .custom-dropdown .Select-control.is-focused {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(1, 135, 95, 0.1);
            }

            /* Radio Items */
            .custom-radio {
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }

            .custom-radio label {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                cursor: pointer;
                padding: 0.75rem;
                border-radius: var(--radius-sm);
                transition: var(--transition);
            }

            .custom-radio label:hover {
                background: rgba(1, 135, 95, 0.05);
            }

            /* Range Slider */
            .custom-slider .rc-slider-track {
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
                height: 6px;
            }

            .custom-slider .rc-slider-handle {
                border: 3px solid var(--primary-color);
                width: 20px;
                height: 20px;
                background: var(--white);
                box-shadow: var(--shadow-md);
            }

            /* Input Section */
            .input-section {
                background: linear-gradient(135deg, rgba(1, 135, 95, 0.05) 0%, rgba(66, 133, 244, 0.05) 100%);
                border-radius: var(--radius-md);
                padding: 1.5rem;
                border: 1px solid rgba(1, 135, 95, 0.1);
            }

            .input-container {
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }

            .input-group {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }

            .input-label {
                font-weight: 600;
                color: var(--gray-700);
            }

            .data-input {
                padding: 0.75rem;
                border: 2px solid var(--gray-300);
                border-radius: var(--radius-sm);
                font-size: 1rem;
                transition: var(--transition);
            }

            .data-input:focus {
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(1, 135, 95, 0.1);
            }

            .add-btn {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                border: none;
                padding: 1rem 2rem;
                border-radius: var(--radius-sm);
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: var(--transition);
                box-shadow: var(--shadow-md);
            }

            .add-btn:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }

            .add-btn:active {
                transform: translateY(0);
            }

            /* Main Content Area */
            .main-content {
                flex: 1;
                background: var(--white);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }

            /* Enhanced Tabs */
            .custom-tabs {
                background: var(--white);
                border-bottom: 1px solid var(--gray-200);
                padding: 0;
            }

            .custom-tabs .tab-content {
                border: none;
            }

            .custom-tab {
                padding: 1rem 2rem !important;
                font-weight: 600 !important;
                color: var(--gray-500) !important;
                border-bottom: 3px solid transparent !important;
                transition: var(--transition) !important;
                background: none !important;
            }

            .custom-tab:hover {
                color: var(--primary-color) !important;
                background: rgba(1, 135, 95, 0.05) !important;
            }

            .custom-tab--selected {
                color: var(--primary-color) !important;
                border-bottom-color: var(--primary-color) !important;
                background: rgba(1, 135, 95, 0.05) !important;
            }

            /* Tab Content */
            .tab-content {
                padding: 2rem;
                flex: 1;
                overflow-y: auto;
            }

            /* Chart Containers */
            .row-charts {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 2rem;
                margin-bottom: 2rem;
            }

            .chart-container {
                background: var(--white);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
                padding: 2rem;
                transition: var(--transition);
                border: 1px solid var(--gray-200);
            }

            .chart-container:hover {
                box-shadow: var(--shadow-lg);
                transform: translateY(-2px);
            }

            .chart-description {
                color: var(--gray-500);
                font-size: 0.95rem;
                margin-top: 1rem;
                padding: 1rem;
                background: var(--gray-100);
                border-radius: var(--radius-sm);
                border-left: 4px solid var(--primary-color);
            }

            /* Table Styles */
            .table-container {
                background: var(--white);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
                padding: 2rem;
                margin: 2rem 0;
                border: 1px solid var(--gray-200);
            }

            .table-title {
                color: var(--gray-900);
                margin-bottom: 1.5rem;
                font-size: 1.3rem;
                font-weight: 700;
            }

            /* Data Table Styles */
            .dash-table-container {
                border-radius: var(--radius-md);
                overflow: hidden;
                box-shadow: var(--shadow-sm);
            }

            .dash-table-container table {
                width: 100%;
            }

            .dash-table-container .cell {
                padding: 1rem !important;
                border-bottom: 1px solid var(--gray-200) !important;
            }

            .dash-table-container .header {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
                color: white !important;
                font-weight: 600 !important;
                text-transform: uppercase !important;
                font-size: 0.85rem !important;
                letter-spacing: 0.5px !important;
            }

            /* Feedback Messages */
            .success-message {
                background: linear-gradient(135deg, var(--success-color), #40e0d0);
                color: white;
                padding: 1rem;
                border-radius: var(--radius-sm);
                margin-top: 1rem;
                display: flex;
                align-items: center;
                font-weight: 500;
                box-shadow: var(--shadow-md);
            }

            .error-message {
                background: linear-gradient(135deg, var(--danger-color), #ff6b6b);
                color: white;
                padding: 1rem;
                border-radius: var(--radius-sm);
                margin-top: 1rem;
                display: flex;
                align-items: center;
                font-weight: 500;
                box-shadow: var(--shadow-md);
            }

            .no-data-message {
                text-align: center;
                padding: 3rem;
                color: var(--gray-500);
                font-size: 1.1rem;
                background: var(--gray-100);
                border-radius: var(--radius-lg);
                margin: 2rem;
            }

            /* Loading States */
            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(1, 135, 95, 0.3);
                border-radius: 50%;
                border-top-color: var(--primary-color);
                animation: spin 1s ease-in-out infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* Responsive Design */
            @media (max-width: 1400px) {
                .row-charts {
                    grid-template-columns: 1fr;
                }
            }

            @media (max-width: 1200px) {
                .dashboard-body {
                    flex-direction: column;
                    gap: 1rem;
                }
                
                .sidebar {
                    width: 100%;
                    position: static;
                }
                
                .metrics-container {
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                }
            }

            @media (max-width: 768px) {
                .dashboard-body {
                    padding: 1rem;
                }
                
                .main-header {
                    padding: 2rem 1rem;
                }
                
                .header-title {
                    font-size: 1.8rem;
                }
                
                .metrics-container {
                    grid-template-columns: 1fr;
                    gap: 1rem;
                }
                
                .metric-card {
                    padding: 1.5rem;
                }
                
                .sidebar {
                    padding: 1.5rem;
                }
                
                .tab-content {
                    padding: 1rem;
                }
                
                .chart-container {
                    padding: 1.5rem;
                }
            }

            @media (max-width: 480px) {
                .metric-card {
                    flex-direction: column;
                    text-align: center;
                    gap: 1rem;
                }
                
                .metric-number {
                    font-size: 2rem;
                }
                
                .header-title i {
                    display: block;
                    margin-bottom: 0.5rem;
                }
            }

            /* Custom Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
            }

            ::-webkit-scrollbar-track {
                background: var(--gray-100);
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb:hover {
                opacity: 0.8;
            }

            /* Focus States for Accessibility */
            button:focus,
            input:focus,
            select:focus {
                outline: 2px solid var(--primary-color);
                outline-offset: 2px;
            }

            /* Print Styles */
            @media print {
                .sidebar {
                    display: none;
                }
                
                .main-content {
                    width: 100%;
                }
                
                .chart-container {
                    break-inside: avoid;
                    box-shadow: none;
                    border: 1px solid var(--gray-300);
                }
                .analysis-section {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    margin-top: 20px;
                }

                .analysis-title {
                    color: #01875f;
                    margin-bottom: 20px;
                }

                .score-container {
                    background: #f9f9f9;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                }

                .score-text {
                    font-size: 18px;
                    font-weight: bold;
                    margin: 10px 0;
                    text-align: center;
                }

                .score-legend {
                    font-size: 12px;
                    color: #666;
                    text-align: center;
                }

                .recommendation-list {
                    padding-left: 20px;
                }

                .recommendation-list li {
                    margin-bottom: 8px;
                }

                .detail-table {
                    width: 100%;
                    border-collapse: collapse;
                }

                .detail-table td {
                    padding: 8px;
                    border-bottom: 1px solid #eee;
                }

                .detail-table td:first-child {
                    font-weight: bold;
                    width: 40%;
                }

                
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''