from typing import Tuple, Union

from .datatypes import HAlign, TextLayout, VAlign


class BlockAligner:
    """テキストを指定サイズの矩形内に配置するときの座標を計算するクラス"""

    def __init__(self, layout: TextLayout, width: float, height: float):
        """`BlockAligner`オブジェクトを初期化する

        Parameters
        ----------
        layout : TextLayout
            配置対象の`TextLayout`オブジェクト
        width : float
            配置先の矩形ブロックの幅
        height : float
            配置先の矩形ブロックの高さ

        """
        self.layout = layout
        self.width = width
        self.height = height

        self._halign: HAlign = HAlign.LEFT
        self._valign: VAlign = VAlign.TOP
        self._padding: Union[float, Tuple[float, ...]] = 0

    def padding(self, px: Union[float, Tuple[float, ...]]) -> "BlockAligner":
        """ブロック内のパディングを設定する

        Parameters
        ----------
        px : Union[float, Tuple[float, ...]]
            パディングの値。floatまたは1, 2, 4要素のタプルで指定する。

        Examples
        --------
        CSSの `padding` プロパティのように値を指定する。

        >>> # 全ての辺に10pxのパディング
        >>> aligner.padding(10)
        >>>
        >>> # 上下に10px, 左右に20pxのパディング
        >>> aligner.padding((10, 20))
        >>>
        >>> # 上10px, 右20px, 下30px, 左40pxのパディング
        >>> aligner.padding((10, 20, 30, 40))

        Returns
        -------
        BlockAligner
            メソッドチェーンのための自分自身のインスタンス

        """
        self._padding = px
        return self

    def alignment(
        self, horizontal: HAlign | None = None, vertical: VAlign | None = None
    ) -> "BlockAligner":
        """水平・垂直方向の配置を設定する

        Parameters
        ----------
        horizontal : HAlign | None, optional
            水平方向の配置（LEFT, CENTER, RIGHT）
        vertical : VAlign | None, optional
            垂直方向の配置（TOP, MIDDLE, BOTTOM）

        Returns
        -------
        BlockAligner
            メソッドチェーンのための自分自身のインスタンス

        """
        if horizontal is not None:
            self._halign = horizontal
        if vertical is not None:
            self._valign = vertical
        return self

    def apply(self) -> TextLayout:
        """設定に基づいて配置を適用し、結果の`TextLayout`を返す。

        注意: このメソッドは、コンストラクタで渡された`TextLayout`オブジェクトを直接変更します。

        Returns
        -------
        TextLayout
            座標が調整された、元の`TextLayout`オブジェクト

        """
        bbox = self.layout.get_content_bbox()
        if bbox is None:
            return self.layout

        _, _, layout_width, layout_height = bbox

        # パディングの解析
        padding_val = self._padding
        if isinstance(padding_val, (int, float)):
            padding_top = padding_right = padding_bottom = padding_left = padding_val
        elif isinstance(padding_val, tuple):
            if len(padding_val) == 1:
                padding_top = padding_right = padding_bottom = padding_left = (
                    padding_val[0]
                )
            elif len(padding_val) == 2:
                padding_top = padding_bottom = padding_val[0]
                padding_right = padding_left = padding_val[1]
            elif len(padding_val) == 4:
                padding_top, padding_right, padding_bottom, padding_left = padding_val
            else:
                raise ValueError(
                    "Padding must be a float or a tuple of 1, 2, or 4 floats."
                )
        else:
            raise TypeError("Padding must be a float or a tuple of floats.")

        drawable_width = self.width - padding_left - padding_right
        drawable_height = self.height - padding_top - padding_bottom

        offset_x = padding_left
        if layout_width < drawable_width:
            if self._halign == HAlign.CENTER:
                offset_x += (drawable_width - layout_width) / 2
            elif self._halign == HAlign.RIGHT:
                offset_x += drawable_width - layout_width

        offset_y = -padding_top
        if layout_height < drawable_height:
            if self._valign == VAlign.MIDDLE:
                offset_y -= (drawable_height - layout_height) / 2
            elif self._valign == VAlign.BOTTOM:
                offset_y -= drawable_height - layout_height

        for line in self.layout.lines:
            for glyph in line.glyphs:
                glyph.x += offset_x
                glyph.y += offset_y

        return self.layout
