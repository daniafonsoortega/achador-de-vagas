create extension if not exists "pgcrypto";

create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text,
  cargo text,
  palavras_chave text,
  localizacao text default 'Barcelona',
  modelo_trabalho text default 'Qualquer'
    check (modelo_trabalho in ('Qualquer', 'Remoto', 'Híbrido', 'Presencial')),
  salario_minimo integer check (salario_minimo is null or salario_minimo >= 0),
  tipo_contrato text default 'Qualquer',
  idiomas text,
  restricoes text,
  curriculo text,
  curriculo_arquivo_nome text,
  curriculo_arquivo_path text,
  privacy_accepted_at timestamptz,
  notifications_paused boolean not null default false,
  connect_code text unique not null default replace(gen_random_uuid()::text, '-', ''),
  telegram_chat_id text unique,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

drop policy if exists "select_own_profile" on public.profiles;
create policy "select_own_profile" on public.profiles for select
  using (auth.uid() = user_id);
drop policy if exists "insert_own_profile" on public.profiles;
create policy "insert_own_profile" on public.profiles for insert
  with check (auth.uid() = user_id);
drop policy if exists "update_own_profile" on public.profiles;
create policy "update_own_profile" on public.profiles for update
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
drop policy if exists "delete_own_profile" on public.profiles;
create policy "delete_own_profile" on public.profiles for delete
  using (auth.uid() = user_id);

create table if not exists public.job_decisions (
  id bigserial primary key,
  user_id uuid not null references public.profiles(user_id) on delete cascade,
  source text not null,
  job_id text not null,
  status text not null check (status in ('rejected', 'sent', 'failed')),
  score numeric(4,2),
  reason text,
  profile_updated_at timestamptz not null,
  decided_at timestamptz not null default now(),
  unique (user_id, source, job_id)
);
alter table public.job_decisions enable row level security;

drop policy if exists "read_own_job_decisions" on public.job_decisions;
create policy "read_own_job_decisions" on public.job_decisions for select
  using (auth.uid() = user_id);

create or replace function public.set_updated_at()
returns trigger language plpgsql set search_path = '' as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists profiles_set_updated_at on public.profiles;
create trigger profiles_set_updated_at before update on public.profiles
  for each row execute function public.set_updated_at();

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'curriculos', 'curriculos', false, 5242880,
  array['application/pdf','application/vnd.openxmlformats-officedocument.wordprocessingml.document','text/plain']
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "upload_own_resume" on storage.objects;
create policy "upload_own_resume" on storage.objects for insert to authenticated
  with check (bucket_id = 'curriculos' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists "read_own_resume" on storage.objects;
create policy "read_own_resume" on storage.objects for select to authenticated
  using (bucket_id = 'curriculos' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists "update_own_resume" on storage.objects;
create policy "update_own_resume" on storage.objects for update to authenticated
  using (bucket_id = 'curriculos' and (storage.foldername(name))[1] = auth.uid()::text)
  with check (bucket_id = 'curriculos' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists "delete_own_resume" on storage.objects;
create policy "delete_own_resume" on storage.objects for delete to authenticated
  using (bucket_id = 'curriculos' and (storage.foldername(name))[1] = auth.uid()::text);

create or replace function public.delete_my_account()
returns void language plpgsql security definer set search_path = '' as $$
declare current_user_id uuid := auth.uid();
begin
  if current_user_id is null then raise exception 'Not authenticated'; end if;
  delete from storage.objects
    where bucket_id = 'curriculos' and (storage.foldername(name))[1] = current_user_id::text;
  delete from auth.users where id = current_user_id;
end;
$$;
revoke all on function public.delete_my_account() from public;
grant execute on function public.delete_my_account() to authenticated;

