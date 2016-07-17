import unittest
from finanse.query.query_parser import QueryLexer
from finanse.query.query_parser import QueryToken
from finanse.query.query_parser import QueryParser
from finanse import QueryParseError


class QueryLexerTest(unittest.TestCase):
    def tokenize(self, text):
        return tuple(QueryLexer().run(text))

    def test_tokenize_tag(self):
        self.assertEqual(
            self.tokenize('test'),
            (QueryToken('tag', 'test'),)
        )

    def test_tokenize_keyword(self):
        self.assertEqual(
            self.tokenize('date'),
            (QueryToken('keyword', 'date'),)
        )

    def test_tokenize_whitespace_operator(self):
        self.assertEqual(
            self.tokenize('and'),
            (QueryToken('operator', 'and'),)
        )

    def test_not_tokenize_whitespace_operator_without_whitespace(self):
        self.assertEqual(
            self.tokenize('testand'),
            (QueryToken('tag', 'testand'),)
        )

    def test_tokenize_single_char_operator(self):
        self.assertEqual(
            self.tokenize('='),
            (QueryToken('operator', '='),)
        )

    def test_tokenize_two_chars_operator(self):
        self.assertEqual(
            self.tokenize('!='),
            (QueryToken('operator', '!='),)
        )

    def test_tokenize_neq(self):
        self.assertEqual(
            self.tokenize('(test)'),
            (
                QueryToken('punctuation', '('),
                QueryToken('tag', 'test'),
                QueryToken('punctuation', ')'),
            )
        )


    def test_tokenize_tag_eq(self):
        self.assertEqual(
            self.tokenize('test ='),
            (
                QueryToken('tag', 'test'),
                QueryToken('operator', '='),
            )
        )

    def test_tokenize_string(self):
        self.assertEqual(
            self.tokenize('"test = and or date"'),
            (
                QueryToken('string', 'test = and or date'),
            )
        )

    def test_tokenize_string2(self):
        self.assertEqual(
            self.tokenize("'test = and or date'"),
            (
                QueryToken('string', 'test = and or date'),
            )
        )

    def test_tokenize_string_and_op(self):
        self.assertEqual(
            self.tokenize('"test = and or date" ='),
            (
                QueryToken('string', 'test = and or date'),
                QueryToken('operator', '='),
            )
        )


class QueryParserTest(unittest.TestCase):
    def parse(self, text):
        return str(QueryParser().run(text))

    def test_parse_single_tag(self):
        self.assertEqual(
            self.parse('test'),
            'test'
        )

    def test_binary(self):
        self.assertEqual(
            self.parse('q or w'),
            '(q or w)'
        )

    def test_unary(self):
        self.assertEqual(
            self.parse('not q'),
            '(not q)'
        )

    def test_missing_right(self):
        with self.assertRaises(QueryParseError) as cm:
            self.parse('test ='),
        self.assertEqual(
            str(cm.exception),
            "can't parse 'test =': unexpected end of query"
        )

    def test_missing_left(self):
        with self.assertRaises(QueryParseError) as cm:
            self.parse('= test'),
        self.assertEqual(
            str(cm.exception),
            "can't parse '= test': missing expression"
        )

    def test_invalid_operator(self):
        with self.assertRaises(QueryParseError) as cm:
            self.parse('test == test'),
        self.assertEqual(
            str(cm.exception),
            "can't parse 'test == test': invalid operator '=='"
        )

    def test_operator_without_spaces(self):
        self.assertEqual(
            self.parse('test=q'),
            '(test = q)'
        )

    def test_unbalanced_right_parenthesis(self):
        with self.assertRaises(QueryParseError) as cm:
            self.parse('(test'),
        self.assertEqual(
            str(cm.exception),
            "can't parse '(test': unbalanced parenthesis"
        )

    def test_unbalanced_left_parenthesis(self):
        with self.assertRaises(QueryParseError) as cm:
            self.parse('test)')
        self.assertEqual(
            str(cm.exception),
            "can't parse 'test)': unbalanced parenthesis"
        )

    def test_unbalanced_string(self):
        with self.assertRaises(QueryParseError) as cm:
            self.parse('"test')
        self.assertEqual(
            str(cm.exception),
            "can't parse query: unexpected end of query"
        )

    def test_single_quote(self):
        with self.assertRaises(QueryParseError) as cm:
            self.parse('"')
        self.assertEqual(
            str(cm.exception),
            "can't parse query: unexpected end of query"
        )

    def test_single_left(self):
        with self.assertRaises(QueryParseError) as cm:
            self.parse('(')
        self.assertEqual(
            str(cm.exception),
            "can't parse '(': unexpected end of query"
        )

    def test_single_right(self):
        with self.assertRaises(QueryParseError) as cm:
            self.parse(')')
        self.assertEqual(
            str(cm.exception),
            "can't parse ')': unbalanced parenthesis"
        )

    def test_parenthesis1(self):
        self.assertEqual(
            self.parse('(q and w) or e and r'),
            '((q and w) or (e and r))'
        )

    def test_parenthesis2(self):
        self.assertEqual(
            self.parse('(q or w) and r'),
            '((q or w) and r)'
        )

    def test_invalid_operator_right(self):
        with self.assertRaises(QueryParseError) as cm:
            self.parse('date = (q or w)')
        self.assertEqual(
            str(cm.exception),
            "can't parse 'date = (q or w)': '(q or w)' can't be on the right side of '=' operator"
        )

    def test_eq_higher_that_or(self):
        self.assertEqual(
            self.parse('date = q or w'),
            '((date = q) or w)'
        )

    def test_invalid_operator_right2(self):
        with self.assertRaises(QueryParseError) as cm:
            self.parse('q = w = r')
        self.assertEqual(
            str(cm.exception),
            "can't parse 'q = w = r': '(q = w)' can't be on the left side of '=' operator"
        )

    'test >= b'


if __name__ == '__main__':
    unittest.main()