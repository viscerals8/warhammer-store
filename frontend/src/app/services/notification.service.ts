import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { Observable, map } from 'rxjs';
import { ConfirmDialogComponent, ConfirmDialogData } from '../components/confirm-dialog/confirm-dialog.component';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  constructor(private snackBar: MatSnackBar, private dialog: MatDialog) {}

  confirm(data: ConfirmDialogData): Observable<boolean> {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data
    });
    return dialogRef.afterClosed().pipe(map(result => !!result));
  }

  success(message: string): void {
    this.snackBar.open(message, 'Cerrar', {
      duration: 3500,
      panelClass: ['wh-snackbar', 'wh-snackbar-success'],
      horizontalPosition: 'center',
      verticalPosition: 'top'
    });
  }

  error(message: string): void {
    this.snackBar.open(message, 'Cerrar', {
      duration: 5000,
      panelClass: ['wh-snackbar', 'wh-snackbar-error'],
      horizontalPosition: 'center',
      verticalPosition: 'top'
    });
  }
}
