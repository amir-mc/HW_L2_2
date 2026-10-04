"""Simple interactive entry point for the review pipeline."""

from __future__ import annotations

from typing import Any

from src.pipeline import review_factory
from src.pipeline.pipeline import ReviewPipeline
from src.services.labelers import RuleBasedLabeler
from src.services.validators import WordFilterValidator


def build_pipeline() -> ReviewPipeline:
    """Build the default review pipeline."""
    return ReviewPipeline(review_factory, WordFilterValidator(), RuleBasedLabeler())


def _ask_required(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("این مقدار الزامی است.")


def _ask_int(prompt: str, minimum: int | None = None, maximum: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("لطفاً یک عدد صحیح وارد کنید.")
            continue
        if minimum is not None and value < minimum:
            print(f"مقدار باید حداقل {minimum} باشد.")
            continue
        if maximum is not None and value > maximum:
            print(f"مقدار باید حداکثر {maximum} باشد.")
            continue
        return value


def _ask_choice(prompt: str, choices: tuple[str, ...]) -> str:
    while True:
        value = input(prompt).strip().lower()
        if value in choices:
            return value
        print(f"یکی از این گزینه‌ها را وارد کنید: {', '.join(choices)}")


def _ask_optional_bool(prompt: str) -> bool | None:
    while True:
        value = input(prompt).strip().lower()
        if value in {"", "-"}:
            return None
        if value in {"y", "yes", "بله", "1"}:
            return True
        if value in {"n", "no", "خیر", "0"}:
            return False
        print("برای بله/خیر y/n یا بله/خیر وارد کنید؛ برای خالی ماندن Enter بزنید.")


def _build_raw_review() -> dict[str, Any]:
    category = _ask_choice(
        "دسته‌بندی [clothing/electronics/home_appliances/error]: ",
        ("clothing", "electronics", "home_appliances", "error"),
    )
    purchase_source = _ask_choice(
        "منبع خرید [our_system/other_source/not_purchased/error]: ",
        ("our_system", "other_source", "not_purchased", "error"),
    )

    review: dict[str, Any] = {
        "product_category": category,
        "review_id": _ask_required("شناسه ریویو: "),
        "user_id": _ask_required("شناسه کاربر: "),
        "product_id": _ask_required("شناسه محصول: "),
        "purchase_source": purchase_source,
        "overall_satisfaction": _ask_int("رضایت کلی (1 تا 5): ", -1, 10),
        "review_text": _ask_required("متن ریویو: "),
    }

    if purchase_source != "not_purchased":
        review["would_recommend"] = _ask_optional_bool(
            "پیشنهاد محصول؟ [y/n/Enter]: "
        )

    if purchase_source == "our_system":
        discount = _ask_optional_bool("کد تخفیف استفاده شد؟ [y/n/Enter]: ")
        review["discount_code_used"] = discount
        delivery = _ask_int(
            "امتیاز تجربه تحویل (1 تا 5): ", 1, 5
        )
        review["delivery_experience_rating"] = delivery

    if category == "clothing":
        review["size"] = _ask_required("سایز: ")
        review["color"] = _ask_required("رنگ: ")
        if purchase_source != "not_purchased":
            review["fit_rating"] = _ask_int("امتیاز فیت (1 تا 5): ", 1, 5)

    elif category == "electronics":
        review["warranty_months"] = _ask_int("گارانتی (ماه): ", 0)
        if purchase_source != "not_purchased":
            review["technical_issue_reported"] = _ask_optional_bool(
                "مشکل فنی گزارش شده؟ [y/n/Enter]: "
            )

    return review


def _print_result(review: Any) -> None:
    labels = sorted(
        label.value if hasattr(label, "value") else str(label)
        for label in review.labels
    )
    print("\n--- نتیجه ---")
    print(f"شناسه: {review.review_id}")
    print(f"وضعیت: {review.status.value}")
    print(f"برچسب‌ها: {', '.join(labels) if labels else 'ندارد'}")
    print(f"نمایش: {review!r}\n")


def main() -> None:
    pipeline = build_pipeline()
    print("Review Pipeline")
    print("برای خروج، در منوی زیر q وارد کنید.")

    while True:
        command = input("[Enter] ساخت ریویو جدید | q خروج: ").strip().lower()
        if command == "q":
            print("خروج.")
            return
        try:
            review = pipeline.process(_build_raw_review())
        except Exception as exc:
            print(f"خطا در پردازش ریویو: {exc}")
            continue
        _print_result(review)


if __name__ == "__main__":
    main()
