import { TestBed, inject } from '@angular/core/testing';

import { SkillService } from './skill.service';

describe('SkillsService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [SkillService]
    });
  });

  it('should be created', inject([SkillService], (service: SkillService) => {
    expect(service).toBeTruthy();
  }));
});
