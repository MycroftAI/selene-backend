import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SkillSearchComponent } from './skill-toolbar.component';

describe('SkillSearchComponent', () => {
  let component: SkillSearchComponent;
  let fixture: ComponentFixture<SkillSearchComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SkillSearchComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SkillSearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
