import { Pipe, PipeTransform } from '@angular/core';

/**
 * Convert bytes into largest possible unit.
 * Takes a precision argument that defaults to 2.
 * Usage:
 *   bytes | fileSize:precision
 * Example:
 *   {{ 1024 | fileSize }}
 *   formats to: 1 KB
 */
@Pipe({
    name: 'fileSize',
    standalone: true
})
export class FileSizePipe implements PipeTransform {
    private readonly units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];

    transform(bytes: number | null | undefined = 0, precision: number = 2): string {
        if (bytes == null || isNaN(parseFloat(String(bytes))) || !isFinite(bytes)) {
            return '?';
        }

        let unit = 0;
        while (bytes >= 1024 && unit < this.units.length - 1) {
            bytes /= 1024;
            unit++;
        }

        return Number(bytes.toPrecision(precision)) + ' ' + this.units[unit];
    }
}
