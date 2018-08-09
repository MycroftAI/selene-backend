import { TestBed, inject } from '@angular/core/testing';

import { HeaderService } from './header.service';

describe('HeaderService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [HeaderService]
    });
  });

  it('should be created', inject([HeaderService], (service: HeaderService) => {
    expect(service).toBeTruthy();
  }));
});
