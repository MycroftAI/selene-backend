import { Component, OnDestroy } from '@angular/core';
import { MediaChange, ObservableMedia } from '@angular/flex-layout';
import { Subscription } from 'rxjs';

export interface SubscriptionType {
    name: string;
    price: string;
    period: string;
}

const nonSupporter: SubscriptionType = {
  name: 'NON-SUPPORTER',
  price: '$0',
  period: null
};
const monthlySupporter: SubscriptionType = {
  name: 'MONTHLY SUPPORTER',
  price: '$1.99',
  period: 'month'
};
const yearlySupporter: SubscriptionType = {
  name: 'YEARLY SUPPORTER',
  price: '$19.99',
  period: 'year'
};


@Component({
  selector: 'account-subscription',
  templateUrl: './subscription.component.html',
  styleUrls: ['./subscription.component.scss']
})
export class SubscriptionComponent implements OnDestroy {
    public subscriptionTypes: SubscriptionType[];
    public subscriptionDate = 'July 10, 2017';
    public alignVertical: boolean;
    private mediaWatcher: Subscription;

  constructor(public media: ObservableMedia) {
      this.mediaWatcher = media.subscribe(
          (change: MediaChange) => {
              this.alignVertical = ['xs', 'sm'].includes(change.mqAlias);
          }
      );
      this.subscriptionTypes = [yearlySupporter, monthlySupporter, nonSupporter];
  }

  ngOnDestroy(): void {
      this.mediaWatcher.unsubscribe();
  }
}
