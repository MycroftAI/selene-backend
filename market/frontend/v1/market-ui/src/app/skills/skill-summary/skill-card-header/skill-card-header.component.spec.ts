import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SkillCardHeaderComponent } from './skill-card-header.component';

describe('SkillCardHeaderComponent', () => {
  let component: SkillCardHeaderComponent;
  let fixture: ComponentFixture<SkillCardHeaderComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SkillCardHeaderComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SkillCardHeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
