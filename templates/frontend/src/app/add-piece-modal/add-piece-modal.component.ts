import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

interface Profile {
  code: string;
  description: string;
  standardLength: number;
  series: string;
}

interface Accessory {
  code: string;
  name: string;
  obligatory: boolean;
}

@Component({
  selector: 'app-add-piece-modal',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatCheckboxModule
  ],
  template: `
    <h2 mat-dialog-title style="margin: 0; padding: 16px 24px; border-bottom: 1px solid var(--text-inactive);">
      Añadir Pieza al Pedido
    </h2>
    <mat-dialog-content style="padding: 24px;">
      <form [formGroup]="pieceForm" (ngSubmit)="onSubmit()">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <!-- Profile selection -->
          <mat-form-field appearance="outline" style="grid-column: span 2;">
            <mat-label>Código de Perfil</mat-label>
            <mat-select formControlName="profileCode" (selectionChange)="onProfileChange($event.value)">
              <mat-option *ngFor="let profile of profiles" [value]="profile.code">
                {{profile.code}} - {{profile.description}}
              </mat-option>
            </mat-select>
            <mat-error *ngIf="pieceForm.get('profileCode')?.hasError('required')">
              Selecciona un perfil
            </mat-error>
          </mat-form-field>

          <!-- Auto-filled description -->
          <mat-form-field appearance="outline" style="grid-column: span 2;">
            <mat-label>Descripción</mat-label>
            <input matInput formControlName="description" readonly>
          </mat-form-field>

          <!-- Quantity -->
          <mat-form-field appearance="outline">
            <mat-label>Cantidad</mat-label>
            <input matInput type="number" formControlName="quantity" min="1" step="1">
            <mat-error *ngIf="pieceForm.get('quantity')?.hasError('required')">
              Introduce la cantidad
            </mat-error>
          </mat-form-field>

          <!-- Tolerance -->
          <mat-form-field appearance="outline">
            <mat-label>Tolerancia</mat-label>
            <mat-select formControlName="tolerance">
              <mat-option value="STANDARD">±0.0015m (Estándar)</mat-option>
              <mat-option value="SPECIAL">±0.0005m (Especial)</mat-option>
            </mat-select>
          </mat-form-field>

          <!-- Length according to rule -->
          <mat-form-field appearance="outline" style="grid-column: span 2;">
            <mat-label>Longitud según Regla (m)</mat-label>
            <input matInput type="number" formControlName="length" step="0.001" min="0">
            <mat-hint>Longitud neta calculada automáticamente</mat-hint>
          </mat-form-field>
        </div>

        <!-- Associated accessories -->
        <div style="margin-top: 24px;">
          <h3 style="margin-bottom: 16px;">Herrajes Asociados</h3>
          <div *ngFor="let accessory of accessories" style="margin-bottom: 8px;">
            <mat-checkbox [checked]="accessory.obligatory" [disabled]="accessory.obligatory">
              {{accessory.code}} - {{accessory.name}}
              <span *ngIf="accessory.obligatory" style="color: var(--color-danger); font-size: 12px;"> (Obligatorio)</span>
            </mat-checkbox>
          </div>
        </div>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end" style="padding: 16px 24px; border-top: 1px solid var(--text-inactive);">
      <button mat-button (click)="onCancel()">Cancelar</button>
      <button mat-flat-button color="primary" (click)="onSubmit()" [disabled]="!pieceForm.valid">
        Guardar Pieza
      </button>
    </mat-dialog-actions>
  `,
  styles: []
})
export class AddPieceModalComponent {
  pieceForm: FormGroup;

  profiles: Profile[] = [
    { code: 'COR-70.01', description: 'Rail superior corredera 70mm', standardLength: 2.450, series: 'COR-70' },
    { code: 'COR-70.03', description: 'Rail inferior corredera 70mm', standardLength: 2.450, series: 'COR-70' },
    { code: '4500.02', description: 'Montante ventana batiente', standardLength: 1.850, series: '4500' },
    { code: '4500.05', description: 'Travesaño ventana batiente', standardLength: 1.200, series: '4500' },
  ];

  accessories: Accessory[] = [
    { code: 'COR-R70', name: 'Rueda corredera 70mm', obligatory: true },
    { code: 'COR-B70', name: 'Banda de estanqueidad', obligatory: false },
    { code: '4500-BIS', name: 'Bisagra ventana batiente', obligatory: true },
    { code: '4500-CER', name: 'Cerradura multipunto', obligatory: false },
  ];

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<AddPieceModalComponent>
  ) {
    this.pieceForm = this.fb.group({
      profileCode: ['', Validators.required],
      description: ['', Validators.required],
      quantity: [1, [Validators.required, Validators.min(1)]],
      tolerance: ['STANDARD', Validators.required],
      length: [0, [Validators.required, Validators.min(0)]]
    });
  }

  onProfileChange(profileCode: string): void {
    const profile = this.profiles.find(p => p.code === profileCode);
    if (profile) {
      this.pieceForm.patchValue({
        description: profile.description,
        length: profile.standardLength
      });
    }
  }

  onSubmit(): void {
    if (this.pieceForm.valid) {
      // In a real app, you would save the piece here
      console.log('Piece data:', this.pieceForm.value);
      this.dialogRef.close(this.pieceForm.value);
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}