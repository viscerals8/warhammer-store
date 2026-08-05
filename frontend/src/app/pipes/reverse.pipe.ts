import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'reverse',
  pure: false
})
export class ReversePipe implements PipeTransform {
  transform<T>(array: T[]): T[] {
    if (!Array.isArray(array)) {
      return array;
    }
    return array.slice().reverse();
  }
}