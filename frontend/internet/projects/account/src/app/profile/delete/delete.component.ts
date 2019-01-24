import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'account-delete',
  templateUrl: './delete.component.html',
  styleUrls: ['./delete.component.scss']
})
export class DeleteComponent implements OnInit {
    public deleteWarning: string[];

  constructor() { }

  ngOnInit() {
      this.deleteWarning = [
          'Pressing the button below will delete your account and all data related to it from Mycroft servers.',
          'It cannot be undone.'
      ];
  }

}
