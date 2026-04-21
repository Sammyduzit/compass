import { logged } from './decorators';
import { UserRepository } from './repository';

export class UserService {
  constructor(private readonly repository = new UserRepository()) {}

  @logged
  async load(id: string) {
    try {
      const user = await this.repository.get(id);
      return user;
    } catch (error) {
      throw new Error('could not load user', { cause: error });
    }
  }
}
