import { Component, OnInit } from '@angular/core';

export interface Subscription {
    name: string;
    price: string;
    period: string;
}

@Component({
  selector: 'account-subscription',
  templateUrl: './subscription.component.html',
  styleUrls: ['./subscription.component.scss']
})
export class SubscriptionComponent implements OnInit {
    public subscriptionTypes: Subscription[];

  constructor() { }

  ngOnInit() {
      // TODO: replace with view call to get values off of table.
      const nonSupporter: Subscription = {
          name: 'NON-SUPPORTER',
          price: '$0',
          period: null
      };
      const monthlySupporter: Subscription = {
          name: 'MONTHLY SUPPORTER',
          price: '$1.99',
          period: 'month'
      };
      const yearlySupporter: Subscription = {
          name: 'YEARLY SUPPORTER',
          price: '$19.99',
          period: 'year'
      };

      this.subscriptionTypes = [yearlySupporter, monthlySupporter, nonSupporter];

  }

}
