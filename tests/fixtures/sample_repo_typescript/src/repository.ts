import type { User } from './types';

export class UserRepository {
  async get(id: string): Promise<User> {
    return { id, name: 'Ada' };
  }
}
