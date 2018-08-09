import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SkillSummaryComponent } from './skill-summary.component';

describe('SkillSummaryComponent', () => {
  let component: SkillSummaryComponent;
  let fixture: ComponentFixture<SkillSummaryComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SkillSummaryComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SkillSummaryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
