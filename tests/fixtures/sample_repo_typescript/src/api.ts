import { UserService } from './service';

export async function handle(id: string) {
  return new UserService().load(id);
}
