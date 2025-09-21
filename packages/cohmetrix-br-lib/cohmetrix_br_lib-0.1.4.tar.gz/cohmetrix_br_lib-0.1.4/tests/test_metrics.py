"""Simple tests for CohMetrix
default features.
"""

import pytest

from cohmetrixBR.features import FEATURES


@pytest.mark.parametrize(
    "text",
    [
        "",
        "Norberto Bobbio, cientista político italiano, afirma que a democracia é um processo que tem, em seu cerne, o objetivo de garantia a representatividade política de todas as pessoas. Para que o mecanismo democrático funcione, então, é fundamental apresentar uma rede estatal que dê acesso a diversos recursos, como alimentação, moradia, educação, segurança, saúde e participação eleitoral. Contudo, muitos brasileiros, por não terem uma certidão de nascimento, são privados desses direitos básicos e têm seus próprios papéis de cidadãos invisibilizados. Logo, deve-se discutir as raízes históricas desse problema e as suas consequências nocivas.",
        "Era uma ves que eu e meus amigo fomos joga bola na rua. A bola era do Joao, mas ele não queria empresta pra todo mundo, só pros amigo dele mais chegado. Eu fiquei meio triste porque queria joga tambem. Ai a bola caiu dentro do quintal da dona Maria que mora do lado da minha casa. Ela tem um cachorro muito bravinho que late pra todo mundo que passa. A gente fico com medo de entra, mas o Joao falo que se a bola fosse dele, tinha que busca.",
    ],
)
def test_extraction(text: str):
    for F in FEATURES:
        _ = F(text)
