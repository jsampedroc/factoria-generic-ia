import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatCheckboxModule } from '@angular/material/checkbox';


interface CuttingRule {
  name: string;
  formula: string;
  profile: string;
  active: boolean;
}

interface DiscountRule {
  minLength: number;
  maxLength: number | null;
  discount: number;
  series: string;
}

@Component({
  selector: 'app-settings-panel',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatTabsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatCheckboxModule
  ],
  template: `
    <h1>Panel de Configuración y Reglas</h1>
    
    <mat-tab-group>
      <!-- Tab 1: Cutting Rules -->
      <mat-tab label="Reglas de Despiece">
        <div style="padding: 24px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
            <h2 style="margin: 0;">Reglas de Despiece</h2>
            <button mat-flat-button color="primary">
              <mat-icon>add</mat-icon>
              Nueva Regla
            </button>
          </div>
          
          <table mat-table [dataSource]="cuttingRules" class="mat-elevation-z2" style="width: 100%;">
            <!-- Name Column -->
            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef> Nombre </th>
              <td mat-cell *matCellDef="let rule"> {{rule.name}} </td>
            </ng-container>
            
            <!-- Formula Column -->
            <ng-container matColumnDef="formula">
              <th mat-header-cell *matHeaderCellDef> Fórmula </th>
              <td mat-cell *matCellDef="let rule"> 
                <span class="mono">{{rule.formula}}</span>
              </td>
            </ng-container>
            
            <!-- Profile Column -->
            <ng-container matColumnDef="profile">
              <th mat-header-cell *matHeaderCellDef> Perfil </th>
              <td mat-cell *matCellDef="let rule"> {{rule.profile}} </td>
            </ng-container>
            
            <!-- Status Column -->
            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef> Estado </th>
              <td mat-cell *matCellDef="let rule">
                <span [style.color]="rule.active ? 'var(--color-secondary)' : 'var(--text-inactive)'">
                  {{rule.active ? 'Activa' : 'Inactiva'}}
                </span>
              </td>
            </ng-container>
            
            <!-- Actions Column -->
            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef> Acciones </th>
              <td mat-cell *matCellDef="let rule">
                <button mat-icon-button>
                  <mat-icon>edit</mat-icon>
                </button>
                <button mat-icon-button>
                  <mat-icon>delete</mat-icon>
                </button>
              </td>
            </ng-container>
            
            <tr mat-header-row *matHeaderRowDef="cuttingRulesColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: cuttingRulesColumns;"></tr>
          </table>
          
          <div style="margin-top: 24px;">
            <h3>Ejemplo de Fórmula</h3>
            <div class="bg-surface" style="padding: 16px; border-radius: var(--border-radius);">
              <div class="mono">L = vano_width + 0.010</div>
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 8px;">
                Donde 'vano_width' es una variable que se captura del formulario de entrada
              </div>
            </div>
          </div>
        </div>
      </mat-tab>
      
      <!-- Tab 2: Discount Tables -->
      <mat-tab label="Tablas de Descuentos">
        <div style="padding: 24px;">
          <h2 style="margin-top: 0;">Tablas de Descuentos por Volumen</h2>
          
          <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; margin-top: 24px;">
            <div *ngFor="let rule of discountRules" class="bg-surface" 
                 style="padding: 16px; border-radius: var(--border-radius);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-weight: 500;">{{rule.series}}</div>
                <div style="font-size: 24px; font-weight: 700; color: var(--color-secondary);">
                  {{rule.discount}}%
                </div>
              </div>
              <div style="font-size: 12px; color: var(--text-secondary);">
                Longitud: {{rule.minLength}}m 
                <span *ngIf="rule.maxLength">- {{rule.maxLength}}m</span>
                <span *ngIf="!rule.maxLength">+</span>
              </div>
            </div>
          </div>
          
          <div style="margin-top: 32px;">
            <h3>Añadir Nueva Regla de Descuento</h3>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
              <mat-form-field appearance="outline">
                <mat-label>Serie</mat-label>
                <mat-select>
                  <mat-option value="COR-70">COR-70</mat-option>
                  <mat-option value="4500">4500</mat-option>
                </mat-select>
              </mat-form-field>
              
              <mat-form-field appearance="outline">
                <mat-label>Longitud Mínima (m)</mat-label>
                <input matInput type="number" min="0" step="0.1">
              </mat-form-field>
              
              <mat-form-field appearance="outline">
                <mat-label>Longitud Máxima (m)</mat-label>
                <input matInput type="number" min="0" step="0.1" placeholder="Opcional">
              </mat-form-field>
              
              <mat-form-field appearance="outline">
                <mat-label>Descuento (%)</mat-label>
                <input matInput type="number" min="0" max="100" step="0.1">
              </mat-form-field>
            </div>
            <button mat-flat-button color="primary" style="margin-top: 16px;">
              Guardar Regla de Descuento
            </button>
          </div>
        </div>
      </mat-tab>
      
      <!-- Tab 3: Stock Management -->
      <mat-tab label="Stock de Barras">
        <div style="padding: 24px;">
          <h2 style="margin-top: 0;">Gestión de Stock de Barras</h2>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 24px;">
            <div>
              <h3>Barras Disponibles</h3>
              <div class="bg-surface" style="padding: 16px; border-radius: var(--border-radius);">
                <div *ngFor="let stock of availableStock" 
                     style="padding: 12px 0; border-bottom: 1px solid var(--text-inactive);">
                  <div style="display: flex; justify-content: space-between;">
                    <span class="mono">{{stock.code}}</span>
                    <span>{{stock.length}}m</span>
                  </div>
                  <div style="font-size: 12px; color: var(--text-secondary);">
                    {{stock.quantity}} unidades
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3>Restos/Offsets Disponibles</h3>
              <div class="bg-surface" style="padding: 16px; border-radius: var(--border-radius);">
                <div *ngFor="let remnant of remnants" 
                     style="padding: 12px 0; border-bottom: 1px solid var(--text-inactive);">
                  <div style="display: flex; justify-content: space-between;">
                    <span class="mono">{{remnant.code}}</span>
                    <span>{{remnant.length}}m</span>
                  </div>
                  <div style="font-size: 12px; color: var(--text-secondary);">
                    ID: {{remnant.id}} · Usar en: {{remnant.useIn}}
                  </div>
                </div>
              </div>
              
              <div style="margin-top: 24px;">
                <h3>Añadir Resto</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                  <mat-form-field appearance="outline">
                    <mat-label>Perfil</mat-label>
                    <mat-select>
                      <mat-option value="COR-70.01">COR-70.01</mat-option>
                      <mat-option value="4500.02">4500.02</mat-option>
                    </mat-select>
                  </mat-form-field>
                  
                  <mat-form-field appearance="outline">
                    <mat-label>Longitud (m)</mat-label>
                    <input matInput type="number" min="0.1" max="6" step="0.001">
                  </mat-form-field>
                </div>
                <button mat-flat-button color="primary" style="margin-top: 16px;">
                  Añadir Resto al Inventario
                </button>
              </div>
            </div>
          </div>
        </div>
      </mat-tab>
      
      <!-- Tab 4: Cutting Preferences -->
      <mat-tab label="Preferencias de Corte">
        <div style="padding: 24px;">
          <h2 style="margin-top: 0;">Preferencias de Corte</h2>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 24px;">
            <div>
              <h3>Tolerancias por Defecto</h3>
              <div class="bg-surface" style="padding: 24px; border-radius: var(--border-radius);">
                <div style="margin-bottom: 16px;">
                  <label style="display: block; margin-bottom: 8px; color: var(--text-secondary);">
                    Tolerancia Estándar (mm)
                  </label>
                  <mat-form-field appearance="outline" style="width: 100%;">
                    <input matInput type="number" value="1.5" step="0.1" min="0">
                    <span matTextSuffix>mm</span>
                  </mat-form-field>
                </div>
                
                <div>
                  <label style="display: block; margin-bottom: 8px; color: var(--text-secondary);">
                    Tolerancia Especial (mm)
                  </label>
                  <mat-form-field appearance="outline" style="width: 100%;">
                    <input matInput type="number" value="0.5" step="0.1" min="0">
                    <span matTextSuffix>mm</span>
                  </mat-form-field>
                </div>
              </div>
            </div>
            
            <div>
              <h3>Otras Preferencias</h3>
              <div class="bg-surface" style="padding: 24px; border-radius: var(--border-radius);">
                <div style="margin-bottom: 16px;">
                  <mat-checkbox checked>Usar algoritmo FFD (First-Fit Decreasing)</mat-checkbox>
                </div>
                
                <div style="margin-bottom: 16px;">
                  <mat-checkbox>Considerar restos en optimización</mat-checkbox>
                </div>
                
                <div style="margin-bottom: 16px;">
                  <mat-checkbox checked>Mostrar advertencias de herrajes obligatorios</mat-checkbox>
                </div>
                
                <div>
                  <mat-checkbox>Auto-guardar cada 5 minutos</mat-checkbox>
                </div>
              </div>
              
              <button mat-flat-button color="primary" style="margin-top: 24px; width: 100%;">
                Guardar Preferencias
              </button>
            </div>
          </div>
        </div>
      </mat-tab>
    </mat-tab-group>
  `,
  styles: []
})
export class SettingsPanelComponent {
  cuttingRulesColumns: string[] = ['name', 'formula', 'profile', 'status', 'actions'];
  
  cuttingRules: CuttingRule[] = [
    { name: 'Vano corredera', formula: 'L = vano_width + 0.010', profile: 'COR-70.01', active: true },
    { name: 'Montante batiente', formula: 'L = altura - 0.015', profile: '4500.02', active: true },
    { name: 'Travesaño fijo', formula: 'L = ancho - 0.020', profile: '4500.05', active: false },
  ];
  
  discountRules: DiscountRule[] = [
    { minLength: 0, maxLength: 50, discount: 0, series: 'COR-70' },
    { minLength: 50, maxLength: 200, discount: 2, series: 'COR-70' },
    { minLength: 200, maxLength: null, discount: 5, series: 'COR-70' },
    { minLength: 0, maxLength: 30, discount: 0, series: '4500' },
    { minLength: 30, maxLength: 100, discount: 1.5, series: '4500' },
  ];
  
  availableStock = [
    { code: 'COR-70.01', length: 6.0, quantity: 42 },
    { code: '4500.02', length: 6.0, quantity: 18 },
    { code: '4500.02', length: 7.0, quantity: 5 },
  ];
  
  remnants = [
    { id: 'R-001', code: 'COR-70.01', length: 1.245, useIn: 'Piezas < 1.5m' },
    { id: 'R-002', code: 'COR-70.01', length: 0.850, useIn: 'No usar' },
    { id: 'R-003', code: '4500.02', length: 2.120, useIn: 'Montantes' },
  ];
}