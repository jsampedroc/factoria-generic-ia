import { Component, Input, OnChanges, SimpleChanges, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-circular-gauge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="gauge-container" #gaugeContainer>
      <svg [attr.width]="size" [attr.height]="size" viewBox="0 0 120 120">
        <!-- Background circle -->
        <circle cx="60" cy="60" r="54" fill="none" stroke="var(--background-surface)" stroke-width="12" />
        
        <!-- Value arc -->
        <circle cx="60" cy="60" r="54" fill="none" 
                [attr.stroke]="color" 
                stroke-width="12" 
                stroke-linecap="round"
                [attr.stroke-dasharray]="circumference"
                [attr.stroke-dashoffset]="dashOffset"
                transform="rotate(-90 60 60)" />
        
        <!-- Center text -->
        <text x="60" y="60" text-anchor="middle" dy="0.3em" 
              style="font-size: 24px; font-weight: 600; fill: var(--text-primary);">
          {{value}}{{unit}}
        </text>
        
        <!-- Label -->
        <text x="60" y="90" text-anchor="middle" 
              style="font-size: 12px; fill: var(--text-secondary);">
          {{label}}
        </text>
      </svg>
    </div>
  `,
  styles: [
    `:host { display: block; }
    .gauge-container { display: inline-block; }
    `
  ]
})
export class CircularGaugeComponent implements OnChanges, AfterViewInit {
  @Input() value: number = 0;
  @Input() max: number = 100;
  @Input() label: string = 'Value';
  @Input() unit: string = '';
  @Input() color: string = 'var(--color-primary)';
  @Input() size: number = 120;
  
  @ViewChild('gaugeContainer') gaugeContainer!: ElementRef;
  
  circumference = 2 * Math.PI * 54; // 2πr where r=54
  dashOffset = this.circumference;
  
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['value'] || changes['max']) {
      this.updateGauge();
    }
  }
  
  ngAfterViewInit(): void {
    this.updateGauge();
  }
  
  private updateGauge(): void {
    const percentage = Math.min(this.value / this.max, 1);
    this.dashOffset = this.circumference * (1 - percentage);
  }
}