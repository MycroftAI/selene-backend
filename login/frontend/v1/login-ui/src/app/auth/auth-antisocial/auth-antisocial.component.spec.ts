import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AuthAntisocialComponent } from './auth-antisocial.component';

describe('AuthAntisocialComponent', () => {
  let component: AuthAntisocialComponent;
  let fixture: ComponentFixture<AuthAntisocialComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AuthAntisocialComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AuthAntisocialComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
