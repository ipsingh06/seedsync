import { Directive, HostListener } from '@angular/core';

@Directive({
    selector: '[appClickStopPropagation]',
    standalone: true
})
export class ClickStopPropagationDirective {
    @HostListener('click', ['$event'])
    onClick(event: Event): void {
        event.stopPropagation();
    }
}
