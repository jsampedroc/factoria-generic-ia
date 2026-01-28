import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatExpansionModule } from '@angular/material/expansion';
import { FormsModule } from '@angular/forms';

interface CutPiece {
  id: string;
  code: string;
  assignedBar: string;
  cutLength: number;
  hardwareRequired: string[];
  hardwareAssigned: boolean[];
  expanded: boolean;
}

@Component({
  selector: 'app-hardware-validation',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatCheckboxModule,
    MatExpansionModule
  ],
  template: `
    <div [style.background]="hasErrors ? 'var(--color-danger)' : 'var(--background-surface)'" 
         style="padding: 16px; border-radius: var(--border-radius); margin-bottom: 24px;">
      <div style="display: flex; align-items: center; gap: 12px;">
        <mat-icon *ngIf="hasErrors" style="color: white;">error</mat-icon>
        <mat-icon *ngIf="!hasErrors" style="color: var(--color-secondary);">check_circle</mat-icon>
        <div>
          <h2 style="margin: 0; color: white;">
            {{hasErrors ? 'ERROR: Faltan 2 x COR-R70 para COR-70.11' : 'Validación de Herrajes'}}
          </h2>
          <p style="margin: 4px 0 0 0; color: rgba(255,255,255,0.8);">
            {{hasErrors ? 'Corrige los herrajes obligatorios faltantes para continuar' : 'Todos los herrajes obligatorios están asignados'}}
          </p>
        </div>
      </div>
    </div>
    
    <h1>Validación y Asignación de Herrajes</h1>
    
    <div class="bg-surface" style="border-radius: var(--border-radius); overflow: hidden;">
      <table mat-table [dataSource]="cutPieces" class="mat-elevation-z0" style="width: 100%;">
        <!-- Code Column -->
        <ng-container matColumnDef="code">
          <th mat-header-cell *matHeaderCellDef> Código Pieza </th>
          <td mat-cell *matCellDef="let piece"> 
            <button mat-icon-button (click)="toggleExpand(piece)" style="margin-right: 8px;">
              <mat-icon>{{piece.expanded ? 'expand_less' : 'expand_more'}}</mat-icon>
            </button>
            <span class="mono">{{piece.code}}</span>
          </td>
        </ng-container>
        
        <!-- Assigned Bar Column -->
        <ng-container matColumnDef="assignedBar">
          <th mat-header-cell *matHeaderCellDef> Barra Asignada </th>
          <td mat-cell *matCellDef="let piece"> {{piece.assignedBar}} </td>
        </ng-container>
        
        <!-- Cut Length Column -->
        <ng-container matColumnDef="cutLength">
          <th mat-header-cell *matHeaderCellDef> Long. Corte </th>
          <td mat-cell *matCellDef="let piece"> <span class="mono">{{piece.cutLength}}m</span> </td>
        </ng-container>
        
        <!-- Hardware Required Column -->
        <ng-container matColumnDef="hardwareRequired">
          <th mat-header-cell *matHeaderCellDef> Herrajes Requeridos </th>
          <td mat-cell *matCellDef="let piece">
            <span *ngFor="let hw of piece.hardwareRequired; let i = index">
              <span [style.color]="piece.hardwareAssigned[i] ? 'var(--color-secondary)' : 'var(--color-danger)'">
                {{hw}}
              </span>
              {{i < piece.hardwareRequired.length - 1 ? ', ' : ''}}
            </span>
          </td>
        </ng-container>
        
        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
        
        <!-- Expanded detail row -->
        <tr *ngFor="let piece of cutPieces" [style.display]="piece.expanded ? 'table-row' : 'none'">
          <td colspan="4" style="padding: 0;">
            <div style="padding: 24px; background: rgba(0,0,0,0.1); border-top: 1px solid var(--text-inactive);">
              <h3 style="margin-top: 0;">Detalles de Herrajes para {{piece.code}}</h3>
              <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px;">
                <div *ngFor="let hw of piece.hardwareRequired; let i = index" 
                     style="padding: 16px; background: rgba(255,255,255,0.05); border-radius: var(--border-radius);">
                  <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <mat-checkbox [(ngModel)]="piece.hardwareAssigned[i]"></mat-checkbox>
                    <div>
                      <div style="font-weight: 500;">{{hw}}</div>
                      <div style="font-size: 12px; color: var(--text-secondary);">
                        {{i === 0 ? 'Obligatorio' : 'Opcional'}}
                      </div>
                    </div>
                  </div>
                  <div style="font-size: 12px; color: var(--text-secondary);">
                    Cantidad: {{i === 0 ? '2' : '1'}} unidad(es) por pieza
                  </div>
                </div>
              </div>
            </div>
          </td>
        </tr>
      </table>
    </div>
    
    <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px;">
      <button mat-stroked-button routerLink="/optimization">
        <mat-icon>arrow_back</mat-icon>
        Volver a Optimización
      </button>
      <button mat-flat-button color="primary" [disabled]="hasErrors" routerLink="/final-summary">
        <mat-icon>check_circle</mat-icon>
        Todo Validado - Continuar
      </button>
    </div>
  `,
  styles: []
})
export class HardwareValidationComponent {
  displayedColumns: string[] = ['code', 'assignedBar', 'cutLength', 'hardwareRequired'];
  
  cutPieces: CutPiece[] = [
    { 
      id: 'A-101', 
      code: 'COR-70.11', 
      assignedBar: 'Barra #1', 
      cutLength: 2.453, 
      hardwareRequired: ['COR-R70', 'COR-B70'],
      hardwareAssigned: [false, true],
      expanded: false
    },
    { 
      id: 'A-102', 
      code: 'COR-70.12', 
      assignedBar: 'Barra #1', 
      cutLength: 2.453, 
      hardwareRequired: ['COR-R70', 'COR-B70'],
      hardwareAssigned: [true, true],
      expanded: false
    },
    { 
      id: 'B-201', 
      code: '4500.21', 
      assignedBar: 'Barra #3', 
      cutLength: 1.853, 
      hardwareRequired: ['4500-BIS', '4500-CER'],
      hardwareAssigned: [true, false],
      expanded: false
    },
  ];
  
  get hasErrors(): boolean {
    return this.cutPieces.some(piece => 
      piece.hardwareRequired.some((hw, i) => 
        hw === 'COR-R70' && !piece.hardwareAssigned[i]
      )
    );
  }
  
  toggleExpand(piece: CutPiece): void {
    piece.expanded = !piece.expanded;
  }
}