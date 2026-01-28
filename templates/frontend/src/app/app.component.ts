import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatMenuModule
  ],
  template: `
    <mat-toolbar class="bg-surface" style="border-bottom: 1px solid var(--text-inactive);">
      <button mat-icon-button aria-label="Menu" class="example-icon" (click)="toggleSidenav()">
        <mat-icon>menu</mat-icon>
      </button>
      <span style="font-weight: 600; font-size: 18px;">Configurador de Corte - Perfiles de Aluminio</span>
      <span class="example-spacer"></span>
      <button mat-icon-button [matMenuTriggerFor]="projectMenu">
        <mat-icon>folder</mat-icon>
      </button>
      <mat-menu #projectMenu="matMenu">
        <button mat-menu-item>
          <mat-icon>add</mat-icon>
          <span>Nuevo Proyecto</span>
        </button>
        <button mat-menu-item>
          <mat-icon>folder_open</mat-icon>
          <span>Abrir Proyecto</span>
        </button>
        <button mat-menu-item>
          <mat-icon>save</mat-icon>
          <span>Guardar Proyecto</span>
        </button>
      </mat-menu>
      <button mat-icon-button [matMenuTriggerFor]="userMenu">
        <mat-icon>account_circle</mat-icon>
      </button>
      <mat-menu #userMenu="matMenu">
        <button mat-menu-item>
          <mat-icon>settings</mat-icon>
          <span>Configuración</span>
        </button>
        <button mat-menu-item>
          <mat-icon>logout</mat-icon>
          <span>Cerrar Sesión</span>
        </button>
      </mat-menu>
    </mat-toolbar>
    <main style="padding: 16px;">
      <router-outlet></router-outlet>
    </main>
    <footer style="position: fixed; bottom: 0; width: 100%; background: var(--background-surface); padding: 8px; text-align: center; font-size: 12px; color: var(--text-secondary);">
      Nesting Configurator v1.0 - Sistema Multi-Tenant para Taller de Nesting 1D
    </footer>
  `,
  styles: [
    `.example-spacer { flex: 1 1 auto; }`
  ]
})
export class AppComponent {
  title = 'nesting-configurator';

  toggleSidenav() {
    // TODO: Implement sidenav toggle logic
    console.log('Toggle sidenav');
  }
}