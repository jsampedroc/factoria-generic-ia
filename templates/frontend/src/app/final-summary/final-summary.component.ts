import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatListModule } from '@angular/material/list';

interface BarCut {
  id: number;
  profileCode: string;
  length: number;
  cuts: Cut[];
  waste: number;
  hardwareNote: string;
}

interface Cut {
  position: number;
  length: number;
  tolerance: number;
  pieceId: string;
}

@Component({
  selector: 'app-final-summary',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    MatListModule
  ],
  template: `
    <h1>Resumen Final e Instrucciones de Corte</h1>
    
    <!-- Section 1: Order Header -->
    <mat-card class="bg-surface" style="margin-bottom: 24px; padding: 24px;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
          <h2 style="margin-top: 0;">Pedido #ORD-2024-00123</h2>
          <div style="color: var(--text-secondary);">
            <div>Cliente: Constructora Moderna S.A.</div>
            <div>Fecha: 15/03/2024</div>
            <div>Proyecto: Edificio Residencial "Las Acacias"</div>
          </div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 12px; color: var(--text-secondary);">Costo Total</div>
          <div style="font-size: 32px; font-weight: 700; color: var(--color-primary);">€5,248.50</div>
          <div style="font-size: 12px; color: var(--color-secondary);">
            Incluye descuento del 3% (€162.25)
          </div>
        </div>
      </div>
    </mat-card>
    
    <!-- Section 2: Cutting List by Bar -->
    <mat-card class="bg-surface" style="margin-bottom: 24px; padding: 24px;">
      <h2 style="margin-top: 0;">Lista de Corte por Barra</h2>
      
      <div *ngFor="let bar of bars" style="margin-bottom: 32px; padding-bottom: 32px; border-bottom: 1px solid var(--text-inactive);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <div>
            <h3 style="margin: 0;">Barra #{{bar.id}} - {{bar.profileCode}} - {{bar.length}}m</h3>
            <div style="color: var(--text-secondary); font-size: 12px;">Código QR: <span class="mono">BAR-{{bar.id}}-{{bar.profileCode}}</span></div>
          </div>
          <div style="width: 100px; height: 100px; background: white; padding: 8px;">
            <!-- QR Code placeholder -->
            <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: black; font-size: 10px;">
              QR CODE
            </div>
          </div>
        </div>
        
        <!-- 1D Visual Diagram -->
        <div style="margin-bottom: 16px;">
          <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">Diagrama 1D de la barra:</div>
          <div style="height: 40px; background: var(--text-inactive); border-radius: 4px; position: relative;">
            <div *ngFor="let cut of bar.cuts" 
                 [style.left.%]="(cut.position / bar.length) * 100"
                 style="position: absolute; top: 0; bottom: 0; width: 2px; background: var(--color-danger);"></div>
            <div *ngFor="let cut of bar.cuts" 
                 [style.left.%]="((cut.position + cut.length) / bar.length) * 100"
                 style="position: absolute; top: 0; bottom: 0; width: 2px; background: var(--color-danger);"></div>
            <div style="position: absolute; top: 0; bottom: 0; right: 0; width: 2px; background: var(--color-danger);"></div>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 10px; color: var(--text-secondary); margin-top: 4px;">
            <span>0m</span>
            <span>{{bar.length}}m</span>
          </div>
        </div>
        
        <!-- Cuts List -->
        <div style="margin-bottom: 16px;">
          <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">Cortes:</div>
          <mat-list dense>
            <mat-list-item *ngFor="let cut of bar.cuts; let i = index">
              <div matListItemTitle>
                {{i + 1}}. {{cut.length * 1000 | number:'1.0-0'}} mm (+{{cut.tolerance * 1000}}mm tolerancia) → Pieza ID: {{cut.pieceId}}
              </div>
            </mat-list-item>
          </mat-list>
        </div>
        
        <!-- Hardware Note -->
        <div style="background: rgba(76, 201, 167, 0.1); padding: 12px; border-radius: var(--border-radius); margin-bottom: 16px;">
          <div style="display: flex; align-items: center; gap: 8px; color: var(--color-secondary);">
            <mat-icon style="font-size: 16px;">build</mat-icon>
            <span><strong>Nota de Herrajes:</strong> {{bar.hardwareNote}}</span>
          </div>
        </div>
        
        <!-- Waste -->
        <div style="color: var(--color-danger); font-size: 12px;">
          <mat-icon style="vertical-align: middle; font-size: 16px;">delete</mat-icon>
          Desperdicio en esta barra: {{bar.waste * 1000}} mm
        </div>
      </div>
    </mat-card>
    
    <!-- Section 3: Materials Plan -->
    <mat-card class="bg-surface" style="margin-bottom: 24px; padding: 24px;">
      <h2 style="margin-top: 0;">Plan de Materiales</h2>
      
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px;">
        <div style="padding: 16px; background: rgba(0,0,0,0.1); border-radius: var(--border-radius);">
          <div style="font-size: 12px; color: var(--text-secondary);">Perfiles Necesarios</div>
          <div style="font-size: 16px; font-weight: 500; margin-top: 8px;">
            20 barras de COR-70.01 (6m)
          </div>
          <div style="font-size: 16px; font-weight: 500; margin-top: 4px; color: var(--color-warning);">
            + 3 barras de 4500.02 (7m, recargo aplicado)
          </div>
        </div>
        
        <div style="padding: 16px; background: rgba(0,0,0,0.1); border-radius: var(--border-radius);">
          <div style="font-size: 12px; color: var(--text-secondary);">Merma Planificada</div>
          <div style="font-size: 24px; font-weight: 700; margin-top: 8px; color: var(--color-danger);">
            2%
          </div>
          <div style="font-size: 12px; color: var(--text-secondary);">Incluida en el total</div>
        </div>
        
        <div style="padding: 16px; background: rgba(0,0,0,0.1); border-radius: var(--border-radius);">
          <div style="font-size: 12px; color: var(--text-secondary);">Tiempo Estimado de Corte</div>
          <div style="font-size: 24px; font-weight: 700; margin-top: 8px;">
            4.5h
          </div>
          <div style="font-size: 12px; color: var(--text-secondary);">Incluye setup y cambios de herramienta</div>
        </div>
      </div>
    </mat-card>
    
    <!-- Final Action Buttons -->
    <div style="display: flex; justify-content: center; gap: 16px; margin-top: 32px;">
      <button mat-flat-button color="primary" style="min-width: 200px;">
        <mat-icon>send</mat-icon>
        Enviar a Máquina de Corte (CNC)
      </button>
      <button mat-stroked-button style="min-width: 200px;">
        <mat-icon>print</mat-icon>
        Imprimir Hojas de Corte
      </button>
      <button mat-stroked-button style="min-width: 200px;">
        <mat-icon>download</mat-icon>
        Exportar PDF/Excel
      </button>
      <button mat-stroked-button style="min-width: 200px;" routerLink="/dashboard">
        <mat-icon>close</mat-icon>
        Cerrar Pedido
      </button>
    </div>
  `,
  styles: []
})
export class FinalSummaryComponent {
  bars: BarCut[] = [
    {
      id: 1,
      profileCode: 'COR-70.01',
      length: 6.0,
      cuts: [
        { position: 0, length: 2.453, tolerance: 0.003, pieceId: 'A-101' },
        { position: 2.453, length: 2.453, tolerance: 0.003, pieceId: 'A-102' },
      ],
      waste: 0.094,
      hardwareNote: 'Instalar 2x COR-R70 en extremos'
    },
    {
      id: 2,
      profileCode: 'COR-70.01',
      length: 6.0,
      cuts: [
        { position: 0, length: 2.453, tolerance: 0.003, pieceId: 'A-103' },
        { position: 2.453, length: 2.453, tolerance: 0.003, pieceId: 'A-104' },
      ],
      waste: 0.094,
      hardwareNote: 'Instalar 2x COR-R70 en extremos'
    },
    {
      id: 3,
      profileCode: '4500.02',
      length: 7.0,
      cuts: [
        { position: 0, length: 1.853, tolerance: 0.003, pieceId: 'B-201' },
        { position: 1.853, length: 1.853, tolerance: 0.003, pieceId: 'B-202' },
        { position: 3.706, length: 1.853, tolerance: 0.003, pieceId: 'B-203' },
      ],
      waste: 0.588,
      hardwareNote: 'Instalar 1x 4500-BIS por pieza'
    },
  ];
}