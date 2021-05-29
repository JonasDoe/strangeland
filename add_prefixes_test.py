import unittest

from add_prefixes import validate_lines, merge_lines


class TestAddPrefixMethods(unittest.TestCase):

    def test_validate(self):
        # old and new version are compatible -> no error will be raised
        _, error = validate_lines(["english text", "german text"], ["&31 english text", ""])
        self.assertIsNone(error)

        # old and new version are compatible -> no error will be raised
        validate_lines(["&31 english text", "&31 german text"], ["&31 english text", ""])

        # old and new version aren't compatible
        _, error = validate_lines(["english text", "german text"], ["&31 english text changed", ""])
        self.assertIsNotNone(error)

        # old version has wrong prefix
        _, error = validate_lines(["&13 english text", "&13 german text"], ["&31 english text changed", ""])
        self.assertIsNotNone(error)

        # old version has different prefixes
        _, error = validate_lines(["&31 english text", "&13 german text"], ["&31 english text changed", ""])
        self.assertIsNotNone(error)

    def test_merge(self):
        # merging adds prefixes where required
        # self.assertEqual(["&31 english text", "&31 german text"],
        #                  merge_lines(["english text", "german text"], ["&31 english text", ""]))

        # merging ignores prefixes where they already exist
        self.assertEqual(["&31 english text", "&31 german text"],
                         merge_lines(["&31 english text", "&31 german text"], ["&31 english text", ""]))

        # merging will override translations in the new file with those from the older ones. Just don't translate stuff
        # in the new file if there's an old version
        self.assertEqual(["&31 english text", "&31 german text"],
                         merge_lines(["&31 english text", "&31 german text"], ["&31 english text", "&31 will be lost"]))

        # merging won't override translation in the new file if there's none in the old file, but the new one will be
        # taken instead
        self.assertEqual(["&31 english text", "&31 won't be lost"],
                         merge_lines(["&31 english text", ""], ["&31 english text", "&31 won't be lost"]))

        # merging won't override translation in the new file if there's none in the old file, but the new one will be
        # taken instead - prefix doesn't count
        self.assertEqual(["&31 english text", "&31 won't be lost"],
                         merge_lines(["&31 english text", "&31 "], ["&31 english text", "&31 won't be lost"]))


if __name__ == '__main__':
    unittest.main()
