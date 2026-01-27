import { Pipe, PipeTransform } from '@angular/core';

/**
 * Convert seconds to an eta in the form "Xh Ym Zs"
 */
@Pipe({
    name: 'eta',
    standalone: true
})
export class EtaPipe implements PipeTransform {
    private readonly units: Record<string, number> = {
        'h': 3600,
        'm': 60,
        's': 1
    };

    transform(seconds: number | null | undefined = 0): string {
        if (seconds == null || isNaN(parseFloat(String(seconds))) || !isFinite(seconds)) {
            return '?';
        }
        if (seconds === 0) {
            return '0s';
        }

        let out = '';
        for (const key of Object.keys(this.units)) {
            const unit = this.units[key];
            if (seconds >= unit) {
                const unitMultiplicity = Math.floor(seconds / unit);
                seconds -= unitMultiplicity * unit;
                out += Number(unitMultiplicity) + key;
            }
        }
        return out;
    }
}
