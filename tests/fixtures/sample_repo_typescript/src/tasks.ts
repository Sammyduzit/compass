import { handle } from './api';

export async function refresh() {
  const user = await handle('ada');
  console.log(user.name);
}
