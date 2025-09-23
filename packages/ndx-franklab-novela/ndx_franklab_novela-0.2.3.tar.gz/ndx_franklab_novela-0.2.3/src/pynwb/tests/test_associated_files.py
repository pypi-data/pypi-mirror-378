from unittest import TestCase

from ndx_franklab_novela import AssociatedFiles


class TestApparatus(TestCase):

    def setUp(self):
        self.associated_files = AssociatedFiles(
            name="file1", description="description of file1", content="1 2 3 content of file test", task_epochs="1, 2"
        )

    def test_successfull_associated_files_creation_true(self):
        self.assertIsInstance(self.associated_files, AssociatedFiles)
        self.assertEqual("file1", self.associated_files.name)
        self.assertEqual("description of file1", self.associated_files.fields["description"])
        self.assertEqual("1 2 3 content of file test", self.associated_files.fields["content"])
        self.assertEqual("1, 2", self.associated_files.fields["task_epochs"])
