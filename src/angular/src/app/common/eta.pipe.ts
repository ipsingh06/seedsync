import { Pipe, PipeTransform } from '@angular/core';

/*
 * Convert seconds to an eta in the form "Xh Ym Zs"
*/
@Pipe({name: 'eta'})
export class EtaPipe implements PipeTransform {

  private units = {
      'h': 3600,
      'm': 60,
      's': 1
  };

  transform(seconds: number = 0) : string {
    if( isNaN( parseFloat( String(seconds) )) || ! isFinite( seconds ) ) return '?';
    if(seconds === 0) return '0s';

    let out: string = '';

    for(let key in this.units) {
        let unit = this.units[key];
        if(seconds >= unit) {
            let unitMultiplicity = Math.floor(seconds/unit);
            seconds -= unitMultiplicity*unit;
            out += Number(unitMultiplicity) + key;
        }
    }
    return out;
  }
}
