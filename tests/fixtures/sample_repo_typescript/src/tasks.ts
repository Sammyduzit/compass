import { handle } from './api';

export async function refresh() {
  await handle('ada');
}
