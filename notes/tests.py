from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Note


class NotesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.list_url = reverse('note-list')
        self.user = User.objects.create_user(username='alice', email='alice@example.com', password='pass1234')
        self.other = User.objects.create_user(username='bob', email='bob@example.com', password='pass5678')

        # Prepare auth headers
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {access}'}

    def create_note_via_api(self, title='A note', content='body', category='random', auth=True):
        data = {'title': title, 'content': content, 'category': category}
        if auth:
            resp = self.client.post(self.list_url, data, content_type='application/json', **self.auth_header)
        else:
            resp = self.client.post(self.list_url, data, content_type='application/json')
        return resp

    def test_list_empty(self):
        resp = self.client.get(self.list_url, **self.auth_header)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

    def test_create_note_requires_auth(self):
        resp = self.create_note_via_api(auth=False)
        # Unauthenticated -> 401 (JWT auth)
        self.assertEqual(resp.status_code, 401)

    def test_create_and_retrieve_note(self):
        resp = self.create_note_via_api(title='Hello', content='World', category='random')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn('id', data)
        note_id = data['id']

        # retrieve detail
        detail_url = reverse('note-detail', args=[note_id])
        r2 = self.client.get(detail_url, **self.auth_header)
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertEqual(d2['title'], 'Hello')
        self.assertEqual(d2['content'], 'World')
        self.assertEqual(d2['category'], 'random')

    def test_update_note(self):
        resp = self.create_note_via_api(title='Old', content='X', category='personal')
        self.assertEqual(resp.status_code, 201)
        note_id = resp.json()['id']
        detail_url = reverse('note-detail', args=[note_id])
        patch_data = {'title': 'New'}
        r = self.client.patch(detail_url, patch_data, content_type='application/json', **self.auth_header)
        self.assertIn(r.status_code, (200, 204))
        # fetch again
        r2 = self.client.get(detail_url, **self.auth_header)
        self.assertEqual(r2.json()['title'], 'New')

    def test_delete_note(self):
        resp = self.create_note_via_api(title='ToDelete', category='school')
        self.assertEqual(resp.status_code, 201)
        note_id = resp.json()['id']
        detail_url = reverse('note-detail', args=[note_id])
        r = self.client.delete(detail_url, **self.auth_header)
        self.assertIn(r.status_code, (204, 200))
        # ensure not found
        r2 = self.client.get(detail_url, **self.auth_header)
        self.assertEqual(r2.status_code, 404)

    def test_counts_and_counts_by_category(self):
        # create multiple notes with different categories
        self.create_note_via_api(title='N1', category='random')
        self.create_note_via_api(title='N2', category='random')
        self.create_note_via_api(title='N3', category='personal')
        # count action
        count_url = self.list_url + 'count/'
        r = self.client.get(count_url, **self.auth_header)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get('count'), 3)
        # counts by category
        cbc_url = self.list_url + 'counts-by-category/'
        r2 = self.client.get(cbc_url, **self.auth_header)
        self.assertEqual(r2.status_code, 200)
        data = r2.json()
        self.assertEqual(data.get('random'), 2)
        self.assertEqual(data.get('personal'), 1)

    def test_user_sees_only_their_notes(self):
        # create a note for other user
        Note.objects.create(title='Bob note', content='x', category='drama', user=self.other)
        # create one for self
        self.create_note_via_api(title='Alice note', category='random')
        r = self.client.get(self.list_url, **self.auth_header)
        self.assertEqual(r.status_code, 200)
        items = r.json()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], 'Alice note')

