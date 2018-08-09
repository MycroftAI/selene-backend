import { HeaderModule } from './header.module';

describe('HeaderModule', () => {
  let toolbarModule: HeaderModule;

  beforeEach(() => {
    toolbarModule = new HeaderModule();
  });

  it('should create an instance', () => {
    expect(toolbarModule).toBeTruthy();
  });
});
