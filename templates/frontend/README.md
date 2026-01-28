# Nesting Configurator - Angular SPA

A visual tactile configurator for 1D nesting workshop, built with Angular 17.

## Features

- Multi-tenant database schema design for industrial profile management
- Visual 3D bar visualization with touch gestures
- Drag-and-drop piece assignment
- Cutting optimization algorithms
- Hardware validation and assignment
- Final cutting instructions with QR codes
- Settings panel for rules and preferences

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/           # Pantalla 1: Dashboard
│   │   ├── add-piece-modal/     # Pantalla 2: Add/Edit Piece Modal
│   │   ├── optimization-view/   # Pantalla 3: Optimization View
│   │   ├── hardware-validation/ # Pantalla 4: Hardware Validation
│   │   ├── final-summary/       # Pantalla 5: Final Summary
│   │   ├── settings-panel/      # Pantalla 6: Settings Panel
│   │   ├── shared/              # Shared components
│   │   │   └── circular-gauge/  # Circular gauge component
│   │   ├── app.component.ts     # Root component
│   │   ├── app.config.ts        # App configuration
│   │   └── app.routes.ts        # Routing configuration
│   ├── assets/                  # Static assets
│   ├── index.html               # Main HTML file
│   ├── main.ts                  # App entry point
│   └── styles.scss              # Global styles
├── angular.json                 # Angular CLI configuration
├── package.json                 # Dependencies and scripts
├── tsconfig.json                # TypeScript configuration
├── Dockerfile                   # Docker configuration
└── README.md                    # This file
```

## Prerequisites

- Node.js 18+ and npm
- Angular CLI 17+

## Installation

1. Clone the repository
2. Navigate to the project directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```

## Development

Run the development server:
```bash
npm start
```

The app will be available at `http://localhost:4200`.

## Build

Build for production:
```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

## Docker

Build and run using Docker:
```bash
docker build -t nesting-configurator .
docker run -p 80:80 nesting-configurator
```

The app will be available at `http://localhost:80`.

## Key Components

### DashboardComponent
Main entry point showing the list of pieces and order summary.

### AddPieceModalComponent
Modal for adding/editing pieces with profile selection and hardware assignment.

### OptimizationViewComponent
Visual optimization interface with 3D viewer, bar list, and optimization controls.

### HardwareValidationComponent
Hardware validation and assignment screen with error alerts.

### FinalSummaryComponent
Final cutting instructions with QR codes and material plans.

### SettingsPanelComponent
Configuration panel for cutting rules, discount tables, stock management, and preferences.

### CircularGaugeComponent
Reusable circular gauge component for displaying metrics.

## Styling

The app uses Angular Material with a custom dark theme based on the industrial style guide:
- Primary background: `#1E1E2E`
- Surface: `#2D2D44`
- Primary color: `#00A8E8` (industrial blue)
- Secondary color: `#4CC9A7` (success green)
- Warning: `#FF9E64` (orange)
- Danger: `#EF476F` (coral red)

## Multi-Tenant Database

The backend database schema supports multi-tenant architecture with:
- Separate schemas per tenant for business data
- Shared schema for reference data (profiles, accessories, rules)
- Tenant isolation with hybrid approach
- PostgreSQL 15+ with JSONB support

## License

Proprietary - Industrial Nesting Configurator System