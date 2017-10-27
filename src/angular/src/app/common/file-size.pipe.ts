import { Pipe, PipeTransform } from '@angular/core';

/*
 * Convert bytes into largest possible unit.
 * Takes an precision argument that defaults to 2.
 * Usage:
 *   bytes | fileSize:precision
 * Example:
 *   {{ 1024 |  fileSize}}
 *   formats to: 1 KB
 * Source: https://gist.github.com/JonCatmull/ecdf9441aaa37
 *         336d9ae2c7f9cb7289a#file-file-size-pipe-ts
*/
@Pipe({name: 'fileSize'})
export class FileSizePipe implements PipeTransform {

  private units = [
    'B',
    'KB',
    'MB',
    'GB',
    'TB',
    'PB'
  ];

  transform(bytes: number = 0, precision: number = 2 ) : string {
    if ( isNaN( parseFloat( String(bytes) )) || ! isFinite( bytes ) ) return '?';

    let unit = 0;

    while ( bytes >= 1024 ) {
      bytes /= 1024;
      unit ++;
    }

    return Number(bytes.toPrecision( + precision )) + ' ' + this.units[ unit ];
  }
}
