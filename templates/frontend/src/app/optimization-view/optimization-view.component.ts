import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSliderModule } from '@angular/material/slider';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { FormsModule } from '@angular/forms';
import { CircularGaugeComponent } from '../shared/circular-gauge/circular-gauge.component';

interface Bar {
  id: number;
  profileCode: string;
  length: number;
  used: number;
  waste: number;
  pieces: string[];
  surcharge: boolean;
}

@Component({
  selector: 'app-optimization-view',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatSliderModule,
    MatSlideToggleModule,
    CircularGaugeComponent
  ],
  template: `
    <h1>Optimización y Configuración Visual</h1>
    
    <div style="display: flex; gap: 16px; height: 70vh;">
      <!-- Left Panel: 3D Visualizer -->
      <div style="flex: 4;" class="bg-surface" style="border-radius: var(--border-radius); padding: 16px;">
        <h2 style="margin-top: 0;">Visualizador 3D Táctil</h2>
        <div style="height: 90%; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.2); border-radius: var(--border-radius);">
          <div style="text-align: center; color: var(--text-secondary);">
            <mat-icon style="font-size: 64px; width: 64px; height: 64px;">3d_rotation</mat-icon>
            <p>Visualizador 3D de barras</p>
            <p>Usa gestos de pellizco para zoom y giro para rotar</p>
          </div>
        </div>
        <div style="margin-top: 16px; display: flex; gap: 8px;">
          <button mat-stroked-button>
            <mat-icon>zoom_in</mat-icon>
            Zoom
          </button>
          <button mat-stroked-button>
            <mat-icon>rotate_left</mat-icon>
            Rotar
          </button>
          <button mat-stroked-button>
            <mat-icon>touch_app</mat-icon>
            Seleccionar Pieza
          </button>
        </div>
      </div>

      <!-- Center Panel: Bars List -->
      <div style="flex: 3.5;" class="bg-surface" style="border-radius: var(--border-radius); padding: 16px; overflow-y: auto;">
        <h2 style="margin-top: 0;">Barras / Cortes</h2>
        <div style="display: flex; gap: 8px; margin-bottom: 16px;">
          <button mat-stroked-button *ngFor="let bar of bars; let i = index" 
                  [style.border-left]="selectedBar === bar.id ? '4px solid var(--color-primary)' : 'none'">
            Barra #{{bar.id}}
          </button>
        </div>
        
        <div *ngFor="let bar of bars" style="margin-bottom: 24px; padding: 16px; background: rgba(0,0,0,0.1); border-radius: var(--border-radius);">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong class="mono">{{bar.profileCode}}</strong>
              <span style="margin-left: 8px; color: var(--text-secondary);">{{bar.length}}m</span>
              <span *ngIf="bar.surcharge" style="margin-left: 8px; color: var(--color-warning);">
                <mat-icon style="vertical-align: middle; font-size: 16px;">warning</mat-icon>
                Recargo 8%
              </span>
            </div>
            <div style="font-size: 12px; color: var(--text-secondary);">
              {{(bar.used/bar.length*100).toFixed(1)}}% utilizado
            </div>
          </div>
          
          <!-- Progress bar -->
          <div style="height: 8px; background: var(--text-inactive); border-radius: 4px; margin: 8px 0; overflow: hidden;">
            <div [style.width.%]="bar.used/bar.length*100" 
                 style="height: 100%; background: var(--color-secondary); float: left;"></div>
            <div [style.width.%]="bar.waste/bar.length*100" 
                 style="height: 100%; background: var(--color-danger); float: left;"></div>
          </div>
          
          <div style="font-size: 12px; color: var(--text-secondary);">
            Piezas: <span *ngFor="let piece of bar.pieces; let last = last">
              {{piece}}{{last ? '' : ', '}}
            </span>
          </div>
        </div>
      </div>

      <!-- Right Panel: Controls and Results -->
      <div style="flex: 2.5;" class="bg-surface" style="border-radius: var(--border-radius); padding: 16px; overflow-y: auto;">
        <h2 style="margin-top: 0;">Control y Resultados</h2>
        
        <div style="margin-bottom: 24px;">
          <mat-slide-toggle [(ngModel)]="use7mBars" style="margin-bottom: 16px;">
            Usar Barras de 7m (con recargo)
          </mat-slide-toggle>
          
          <div>
            <label style="display: block; margin-bottom: 8px; color: var(--text-secondary);">
              Prioridad: Ahorro Material vs. Ahorro Coste
            </label>
            <mat-slider min="0" max="100" step="1" [(ngModel)]="prioritySlider">
              <input matSliderThumb>
            </mat-slider>
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-secondary);">
              <span>Material</span>
              <span>Coste</span>
            </div>
          </div>
        </div>
        
        <!-- Optimization Results -->
        <div style="margin-bottom: 24px;">
          <h3>Resultados de Optimización</h3>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
            <app-circular-gauge 
              [value]="94" 
              [max]="100" 
              [label]="'Utilización'" 
              [unit]="'%'"
              [color]="'var(--color-secondary)'">
            </app-circular-gauge>
            
            <app-circular-gauge 
              [value]="3" 
              [max]="10" 
              [label]="'Descuento'" 
              [unit]="'%'"
              [color]="'var(--color-primary)'">
            </app-circular-gauge>
          </div>
          
          <div style="background: rgba(0,0,0,0.1); padding: 12px; border-radius: var(--border-radius); margin-bottom: 8px;">
            <div style="font-size: 12px; color: var(--text-secondary);">Barras Totales</div>
            <div style="font-size: 24px; font-weight: 600;">24</div>
          </div>
          
          <div style="background: rgba(0,0,0,0.1); padding: 12px; border-radius: var(--border-radius); margin-bottom: 8px;">
            <div style="font-size: 12px; color: var(--text-secondary);">Costo Material Estimado</div>
            <div style="font-size: 24px; font-weight: 600;">€4,850.75</div>
          </div>
          
          <div style="background: rgba(0,0,0,0.1); padding: 12px; border-radius: var(--border-radius);">
            <div style="font-size: 12px; color: var(--text-secondary);">Desperdicio Total</div>
            <div style="font-size: 24px; font-weight: 600; color: var(--color-danger);">2.45 m</div>
          </div>
        </div>
        
        <button mat-flat-button color="primary" style="width: 100%;" routerLink="/hardware-validation">
          <mat-icon>check_circle</mat-icon>
          Aplicar Optimización y Bloquear
        </button>
      </div>
    </div>
    
    <!-- Floating piece list for drag & drop -->
    <div style="position: fixed; bottom: 80px; right: 24px; width: 300px;" class="bg-surface" 
         style="border-radius: var(--border-radius); padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
      <h3 style="margin-top: 0;">Piezas sin Asignar</h3>
      <div *ngFor="let piece of unassignedPieces" 
           style="padding: 12px; margin-bottom: 8px; background: rgba(0,168,232,0.1); border-radius: var(--border-radius); cursor: move;"
           draggable="true">
        <div style="display: flex; justify-content: space-between;">
          <span class="mono">{{piece.code}}</span>
          <span>{{piece.length}}m</span>
        </div>
        <div style="font-size: 12px; color: var(--text-secondary);">{{piece.description}}</div>
      </div>
    </div>
  `,
  styles: []
})
export class OptimizationViewComponent {
  use7mBars = false;
  prioritySlider = 50;
  selectedBar = 1;
  
  bars: Bar[] = [
    { id: 1, profileCode: 'COR-70.01', length: 6.0, used: 5.65, waste: 0.35, pieces: ['COR-70.01-1', 'COR-70.01-2'], surcharge: false },
    { id: 2, profileCode: 'COR-70.01', length: 6.0, used: 5.72, waste: 0.28, pieces: ['COR-70.01-3', 'COR-70.01-4'], surcharge: false },
    { id: 3, profileCode: '4500.02', length: 7.0, used: 6.45, waste: 0.55, pieces: ['4500.02-1', '4500.02-2'], surcharge: true },
  ];
  
  unassignedPieces = [
    { code: 'COR-70.03', description: 'Rail inferior', length: 2.45 },
    { code: '4500.05', description: 'Travesaño', length: 1.20 },
  ];
}