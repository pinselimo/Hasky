module TypeParser where

import Text.Parsec
import qualified Text.Parsec.Token as P
import Text.Parsec.Language (haskell, haskellDef)
import Text.Parsec.String

import HTypes (HType(..), htype)

data TypeDef = TypeDef {
    funcN :: String,
    funcT :: [HType]
    } deriving (Show, Eq)

parseTypeDef :: Parser TypeDef
parseTypeDef = do
  fname <- funcName
  types <- typeDef *> parseTypes
  return $ TypeDef fname types

parseTypes :: Parser [HType]
parseTypes = skip *> sepBy1 (parseType <* skip) (arrow <* skip)

parseType :: Parser HType
parseType = func <|> tuple <|> list <|> io <|> unit <|> htype

typeConstr = funcName *> barrow

strip x = skip *> x <* skip
skip = skipMany space

io = try iomonad *> parseType >>= return . HIO
unit = parens skip >> return HUnit
func = try $ lookAhead isFunc *> parens (sepBy1 (strip parseType) (strip arrow))  >>= return . HFunc
tuple = try $ lookAhead isTuple *> parens (commaSep $ strip parseType) >>= return . HTuple
list = brackets (strip parseType) >>= return . HList

-- Checkers:
isFunc = lookAhead $ parens (identifier *> many1 (strip $ arrow *> parseType))
isTuple = lookAhead $ parens (parseType *> many1 (strip $ comma *> parseType))
isTypeDef = lookAhead $ identifier *> typeDef

-- Lexer:
lexer = P.makeTokenParser haskellDef

commaSep = P.commaSep lexer
parens = P.parens lexer
brackets = P.brackets lexer
barrow = (P.reservedOp lexer) "=>"
arrow = (P.reservedOp lexer) "->"
iomonad = (P.reservedOp lexer) "IO"
typeDef = (P.reservedOp lexer) "::"
comma = P.comma lexer
funcName = P.identifier lexer
identifier = P.identifier lexer
