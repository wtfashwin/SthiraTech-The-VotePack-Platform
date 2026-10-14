import assert from 'node:assert/strict';
import { test } from 'node:test';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from '../src/pages/LoginPage';
import RegisterPage from '../src/pages/RegisterPage';
import { Button } from '../src/components/ui/button';

test('login exposes email, password and submit controls', () => {
  const html = renderToStaticMarkup(<MemoryRouter><LoginPage /></MemoryRouter>);
  assert.match(html, /id="email"[^>]*type="email"|type="email"[^>]*id="email"/);
  assert.match(html, /type="password"/);
  assert.match(html, /type="submit"/);
  assert.match(html, /Sign In/);
});

test('registration exposes password confirmation and sign-in link', () => {
  const html = renderToStaticMarkup(<MemoryRouter><RegisterPage /></MemoryRouter>);
  assert.match(html, /name="confirmPassword"/);
  assert.match(html, /type="submit"/);
  assert.match(html, /href="\/login"/);
  assert.match(html, /Create Account/);
});

test('submit button renders disabled while loading', () => {
  const html = renderToStaticMarkup(<Button type="submit" isLoading>Pay</Button>);
  assert.match(html, /disabled=""/);
  assert.match(html, /Loading/);
  assert.doesNotMatch(html, />Pay</);
});
