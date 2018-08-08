import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AuthSocialComponent } from './auth-social.component';

describe('AuthSocialComponent', () => {
  let component: AuthSocialComponent;
  let fixture: ComponentFixture<AuthSocialComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AuthSocialComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AuthSocialComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
