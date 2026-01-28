import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatDialog } from '@angular/material/dialog';
import { AddPieceModalComponent } from '../add-piece-modal/add-piece-modal.component';
import { MatMenuModule } from '@angular/material/menu';


interface Piece {
  code: string;
  description: string;
  netLength: number;
  quantity: number;
  series: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatMenuModule
  ],
  template: `
    <div style="display: flex; gap: 24px;">
      <!-- Main content -->
      <div style="flex: 3;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
          <h1>Dashboard - Entrada del Pedido</h1>
          <div>
            <button mat-stroked-button style="margin-right: 8px;">
              <mat-icon>filter_list</mat-icon>
              Filtrar
            </button>
            <button mat-flat-button color="primary" (click)="openAddPieceModal()">
              <mat-icon>add</mat-icon>
              Añadir Pieza
            </button>
          </div>
        </div>

        <!-- Pieces table -->
        <div class="bg-surface" style="padding: 16px; border-radius: var(--border-radius);">
          <table mat-table [dataSource]="pieces" class="mat-elevation-z2" style="width: 100%;">
            <!-- Code Column -->
            <ng-container matColumnDef="code">
              <th mat-header-cell *matHeaderCellDef> Código </th>
              <td mat-cell *matCellDef="let piece"> <span class="mono">{{piece.code}}</span> </td>
            </ng-container>

            <!-- Description Column -->
            <ng-container matColumnDef="description">
              <th mat-header-cell *matHeaderCellDef> Descripción </th>
              <td mat-cell *matCellDef="let piece"> {{piece.description}} </td>
            </ng-container>

            <!-- Net Length Column -->
            <ng-container matColumnDef="netLength">
              <th mat-header-cell *matHeaderCellDef> Long. Neta (m) </th>
              <td mat-cell *matCellDef="let piece"> <span class="mono">{{piece.netLength | number:'1.3-3'}}</span> </td>
            </ng-container>

            <!-- Quantity Column -->
            <ng-container matColumnDef="quantity">
              <th mat-header-cell *matHeaderCellDef> Cant. </th>
              <td mat-cell *matCellDef="let piece"> {{piece.quantity}} </td>
            </ng-container>

            <!-- Actions Column -->
            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef> Acciones </th>
              <td mat-cell *matCellDef="let piece">
                <button mat-icon-button [matMenuTriggerFor]="menu">
                  <mat-icon>more_vert</mat-icon>
                </button>
                <mat-menu #menu="matMenu">
                  <button mat-menu-item>
                    <mat-icon>edit</mat-icon>
                    <span>Editar</span>
                  </button>
                  <button mat-menu-item>
                    <mat-icon>content_copy</mat-icon>
                    <span>Duplicar</span>
                  </button>
                  <button mat-menu-item style="color: var(--color-danger);">
                    <mat-icon>delete</mat-icon>
                    <span>Eliminar</span>
                  </button>
                </mat-menu>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
          </table>
        </div>
      </div>

      <!-- Sidebar -->
      <div style="flex: 1;">
        <mat-card class="bg-surface" style="padding: 16px; margin-bottom: 16px;">
          <h2 style="margin-top: 0;">Resumen del Pedido</h2>
          <div style="text-align: center; margin: 24px 0;">
            <div style="font-size: 48px; font-weight: 700; color: var(--color-primary);">
              {{totalLength | number:'1.1-1'}}
            </div>
            <div class="text-secondary">Longitud Total (m)</div>
          </div>
          <div>
            <h3>Series Presentes</h3>
            <ul style="list-style: none; padding: 0;">
              <li *ngFor="let series of presentSeries" style="padding: 8px 0; border-bottom: 1px solid var(--text-inactive);">
                <span class="mono">{{series}}</span>
              </li>
            </ul>
          </div>
          <button mat-flat-button color="primary" style="width: 100%; margin-top: 24px;" routerLink="/optimization">
            <mat-icon>optimize</mat-icon>
            Validar y Optimizar
          </button>
        </mat-card>
      </div>
    </div>
  `,
  styles: []
})
export class DashboardComponent implements OnInit {
  displayedColumns: string[] = ['code', 'description', 'netLength', 'quantity', 'actions'];
  pieces: Piece[] = [
    { code: 'COR-70.01', description: 'Rail superior corredera 70mm', netLength: 2.450, quantity: 12, series: 'COR-70' },
    { code: '4500.02', description: 'Montante ventana batiente', netLength: 1.850, quantity: 8, series: '4500' },
    { code: 'COR-70.03', description: 'Rail inferior corredera 70mm', netLength: 2.450, quantity: 12, series: 'COR-70' },
  ];

  get totalLength(): number {
    return this.pieces.reduce((sum, piece) => sum + (piece.netLength * piece.quantity), 0);
  }

  get presentSeries(): string[] {
    return [...new Set(this.pieces.map(p => p.series))];
  }

  constructor(private dialog: MatDialog) {}

  ngOnInit(): void {}

  openAddPieceModal(): void {
    this.dialog.open(AddPieceModalComponent, {
      width: '600px',
      maxHeight: '90vh'
    });
  }
}