#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Usage: tests/fixtures/setup.sh [all|sample_repo_minimal|sample_repo_python|sample_repo_typescript]

Recreates synthetic fixture repositories with scripted git history.
Running the script repeatedly is safe: each selected fixture is deleted
and rebuilt from scratch.
EOF
}

reset_repo() {
  local repo_name="$1"
  rm -rf "${ROOT_DIR:?}/${repo_name}"
  mkdir -p "${ROOT_DIR}/${repo_name}"
  git -C "${ROOT_DIR}/${repo_name}" init --quiet
  git -C "${ROOT_DIR}/${repo_name}" config user.name "Compass Fixtures"
  git -C "${ROOT_DIR}/${repo_name}" config user.email "fixtures@compass.local"
}

commit_all() {
  local repo_name="$1"
  local message="$2"
  git -C "${ROOT_DIR}/${repo_name}" add .
  git -C "${ROOT_DIR}/${repo_name}" commit --quiet -m "${message}"
}

write_file() {
  local path="$1"
  mkdir -p "$(dirname "${path}")"
  printf '%s\n' "${@:2}" > "${path}"
}

setup_minimal() {
  local repo="sample_repo_minimal"
  reset_repo "${repo}"
  write_file "${ROOT_DIR}/${repo}/README.md" "# Minimal Fixture" "" "A tiny generic repo."
  write_file "${ROOT_DIR}/${repo}/notes.txt" "first note"
  commit_all "${repo}" "feat: add minimal fixture"
  write_file "${ROOT_DIR}/${repo}/config.ini" "[fixture]" "name = minimal"
  commit_all "${repo}" "chore: add fixture config"
}

setup_python() {
  local repo="sample_repo_python"
  reset_repo "${repo}"
  mkdir -p "${ROOT_DIR}/${repo}/src/sample_app" "${ROOT_DIR}/${repo}/tests"
  write_file "${ROOT_DIR}/${repo}/CONTRIBUTING.md" "# Contributing" "" "Prefer explicit errors and small modules."
  write_file "${ROOT_DIR}/${repo}/README.md" "# Python Fixture"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/__init__.py" "from .service import UserService as UserService"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/config.py" "from dataclasses import dataclass" "" "@dataclass(frozen=True)" "class Settings:" "    retries: int = 3"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/errors.py" "class AppError(Exception):" "    pass"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/models.py" "class User:" "    def __init__(self, name: str) -> None:" "        self.name = name" "" "    @property" "    def slug(self) -> str:" "        return self.name.lower().replace(' ', '-')"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/repository.py" "from .models import User" "" "class UserRepository:" "    def get(self, name: str) -> User:" "        return User(name)"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/service.py" "from collections.abc import Callable" "" "from .models import User" "from .repository import UserRepository" "" "def audited(func: Callable[[object, str], User]) -> Callable[[object, str], User]:" "    return func" "" "class UserService:" "    def __init__(self) -> None:" "        self.repository = UserRepository()" "" "    @staticmethod" "    def normalize(name: str) -> str:" "        return name.strip()" "" "    @audited" "    def load(self, name: str) -> User:" "        try:" "            return self.repository.get(self.normalize(name))" "        except ValueError as exc:" "            raise RuntimeError('could not load user') from exc"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/api.py" "from .models import User" "from .service import UserService" "" "def handle(name: str) -> User:" "    return UserService().load(name)"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/cli.py" "from .api import handle" "" "def main() -> None:" "    handle('Ada')"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/cache.py" "CACHE: dict[str, str] = {}"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/events.py" "def publish(event: str) -> None:" "    print(event)"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/validators.py" "def require_name(name: str) -> None:" "    if not name:" "        raise ValueError('name is required')"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/tasks.py" "from .service import UserService" "" "def refresh() -> None:" "    UserService().load('Grace')"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/utils.py" "def join_words(words: list[str]) -> str:" "    return ' '.join(words)"
  write_file "${ROOT_DIR}/${repo}/tests/test_service.py" "from sample_app.service import UserService" "" "def test_normalize() -> None:" "    assert UserService.normalize(' Ada ') == 'Ada'"
  write_file "${ROOT_DIR}/${repo}/pyproject.toml" "[project]" "name = 'sample-app'" "version = '0.1.0'"
  commit_all "${repo}" "feat: add python fixture app"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/service.py" "from collections.abc import Callable" "" "from .models import User" "from .repository import UserRepository" "" "def audited(func: Callable[[object, str], User]) -> Callable[[object, str], User]:" "    return func" "" "class UserService:" "    def __init__(self) -> None:" "        self.repository = UserRepository()" "" "    @staticmethod" "    def normalize(name: str) -> str:" "        return name.strip()" "" "    @audited" "    def load(self, name: str) -> User:" "        try:" "            user = self.repository.get(self.normalize(name))" "            return user" "        except ValueError as exc:" "            raise RuntimeError('could not load user') from exc"
  commit_all "${repo}" "fix: update hot service path"
  write_file "${ROOT_DIR}/${repo}/src/sample_app/tasks.py" "from .service import UserService" "" "def refresh() -> None:" "    user = UserService().load('Grace')" "    print(user.slug)"
  commit_all "${repo}" "feat: add background refresh logging"
}

setup_typescript() {
  local repo="sample_repo_typescript"
  reset_repo "${repo}"
  mkdir -p "${ROOT_DIR}/${repo}/src" "${ROOT_DIR}/${repo}/tests"
  write_file "${ROOT_DIR}/${repo}/CONTRIBUTING.md" "# Contributing" "" "Prefer async boundaries and typed interfaces."
  write_file "${ROOT_DIR}/${repo}/README.md" "# TypeScript Fixture"
  write_file "${ROOT_DIR}/${repo}/package.json" '{"name":"sample-ts","version":"0.1.0","type":"module"}'
  write_file "${ROOT_DIR}/${repo}/tsconfig.json" '{"compilerOptions":{"strict":true,"target":"ES2022"}}'
  write_file "${ROOT_DIR}/${repo}/src/types.ts" "export interface User {" "  id: string;" "  name: string;" "}"
  write_file "${ROOT_DIR}/${repo}/src/errors.ts" "export class AppError extends Error {}"
  write_file "${ROOT_DIR}/${repo}/src/decorators.ts" "export function logged(_: unknown, _key: string, descriptor: PropertyDescriptor) {" "  return descriptor;" "}"
  write_file "${ROOT_DIR}/${repo}/src/repository.ts" "import type { User } from './types';" "" "export class UserRepository {" "  async get(id: string): Promise<User> {" "    return { id, name: 'Ada' };" "  }" "}"
  write_file "${ROOT_DIR}/${repo}/src/service.ts" "import { logged } from './decorators';" "import { UserRepository } from './repository';" "" "export class UserService {" "  constructor(private readonly repository = new UserRepository()) {}" "" "  @logged" "  async load(id: string) {" "    try {" "      return await this.repository.get(id);" "    } catch (error) {" "      throw new Error('could not load user', { cause: error });" "    }" "  }" "}"
  write_file "${ROOT_DIR}/${repo}/src/api.ts" "import { UserService } from './service';" "" "export async function handle(id: string) {" "  return new UserService().load(id);" "}"
  write_file "${ROOT_DIR}/${repo}/src/index.ts" "export { handle } from './api';"
  write_file "${ROOT_DIR}/${repo}/src/cache.ts" "export const cache = new Map<string, string>();"
  write_file "${ROOT_DIR}/${repo}/src/events.ts" "export function publish(event: string): void {" "  console.log(event);" "}"
  write_file "${ROOT_DIR}/${repo}/src/validators.ts" "export function requireId(id: string): void {" "  if (!id) throw new Error('id is required');" "}"
  write_file "${ROOT_DIR}/${repo}/src/tasks.ts" "import { handle } from './api';" "" "export async function refresh() {" "  await handle('ada');" "}"
  write_file "${ROOT_DIR}/${repo}/src/utils.ts" "export function joinWords(words: string[]): string {" "  return words.join(' ');" "}"
  write_file "${ROOT_DIR}/${repo}/tests/service.test.ts" "import { UserService } from '../src/service';" "" "void new UserService().load('ada');"
  commit_all "${repo}" "feat: add typescript fixture app"
  write_file "${ROOT_DIR}/${repo}/src/service.ts" "import { logged } from './decorators';" "import { UserRepository } from './repository';" "" "export class UserService {" "  constructor(private readonly repository = new UserRepository()) {}" "" "  @logged" "  async load(id: string) {" "    try {" "      const user = await this.repository.get(id);" "      return user;" "    } catch (error) {" "      throw new Error('could not load user', { cause: error });" "    }" "  }" "}"
  commit_all "${repo}" "fix: update hot service path"
  write_file "${ROOT_DIR}/${repo}/src/tasks.ts" "import { handle } from './api';" "" "export async function refresh() {" "  const user = await handle('ada');" "  console.log(user.name);" "}"
  commit_all "${repo}" "feat: log background refresh result"
}

main() {
  local target="${1:-all}"

  case "${target}" in
    all)
      setup_minimal
      setup_python
      setup_typescript
      ;;
    sample_repo_minimal)
      setup_minimal
      ;;
    sample_repo_python)
      setup_python
      ;;
    sample_repo_typescript)
      setup_typescript
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage >&2
      echo "Unknown fixture target: ${target}" >&2
      return 1
      ;;
  esac
}

main "$@"
