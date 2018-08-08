import { AuthModule } from './auth.module';

describe('AuthModule', () => {
  let authenticateModule: AuthModule;

  beforeEach(() => {
    authenticateModule = new AuthModule();
  });

  it('should create an instance', () => {
    expect(authenticateModule).toBeTruthy();
  });
});
