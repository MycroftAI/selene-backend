import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SkillDetailComponent } from './skill-detail.component';

describe('SkillDetailComponent', () => {
  let component: SkillDetailComponent;
  let fixture: ComponentFixture<SkillDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SkillDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SkillDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
